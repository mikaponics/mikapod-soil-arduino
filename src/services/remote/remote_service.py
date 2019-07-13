#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import signal
import time

import Pyro4
import serpent

from foundation import *
from mikaponics_api import *


"""
Application used to communicate with the remote API web-service and do the
following:

(1) Fetch an access token based on the oAuth 2.0 client-credentials.
(2) Poll available time-series data from the persistent storage and submit
    it to the API web-service using the oAuth 2.0 credentials provided.
(3) Remove the time-series data from our local persistent storage that we
    successfully submitted.
"""

class ServiceExit(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """
    pass


def onServiceShutdownHandler(signum, frame):
    """
    Function to be called by our `SIGINT` and `SIGTERM` handlers.
    """
    print("-------------------------------------------------------------------")
    print(getDT(), '| REMOTE | Caught signal %d' % signum)
    print("-------------------------------------------------------------------")
    raise ServiceExit


def onTokenRefreshedHandler(token):
    """
    Function will be fired by the ``MikaponicsAPI`` class when a token has
    expired and provided a new token.
    """
    service = RemoteServiceApp.getInstance()
    print("REFRESH:", token)


class RemoteServiceApp(object):

    def __init__(self):
        # Load up the API interface along with integrating a callback
        self.__mikaponicsAPI = MikaponicsAPI.getInstance()
        self.__mikaponicsAPI.beginOperation(onTokenRefreshedHandler)
        self.__storage = Pyro4.Proxy("PYRONAME:mikapod.storage")
        self.__token = None

    def beginOperation(self):
        print(getDT(), "| REMOTE | Setting up.")
        self.__token = self.__storage.getValueFromKeyValueItemByKey(ACCESS_TOKEN_KEY)

        print(getDT(), "| REMOTE | Register the signal handlers.")
        signal.signal(signal.SIGTERM, onServiceShutdownHandler)
        signal.signal(signal.SIGINT, onServiceShutdownHandler)

    def runOnMainLoop(self):
        """
        Function is the main loop of the application.
        """
        try:
            print(getDT(), "| REMOTE | Starting main program.")
            self.runOperationLoop()
        except ServiceExit:
            print(getDT(), "| REMOTE | Gracefully shutting down.")
        print(getDT(), "| REMOTE | Exiting main program.")

    def runOperationLoop(self):
        # STEP 1: Focus the main runtime loop on attempting to fetch the
        #         latest access token from the API server.
        self.runFetchTokenOperationLoop()

        # STEP 2: Focus the main runtime loop on continously checking the
        #         local persistent storage and uploading the time series data
        #         to the API.
        self.runDataUploadOperationLoop()

    def runFetchTokenOperationLoop(self):
        while self.__token is None:
            self.runFetchTokenOperation()
            time.sleep(1)

    def runDataUploadOperationLoop(self):
        while True:
            # Run a single loop.
            self.runDataUploadOperation()

            # Add artificial delay so we are not hammering the API server.
            # Essentially we are doing this so the server does not get
            # have too much to handle. The value is arbitrarly chosen,
            # please adjust if necessary.
            print(getDT(), "| REMOTE | Artificial wait. please wait...")
            time.sleep(10)

    def runFetchTokenOperation(self):
        token, wasSuccess = self.__mikaponicsAPI.getAPIToken()
        if wasSuccess:
            self.__token = token
            self.__storage.setKeyValueItem(ACCESS_TOKEN_KEY, token)

    def runDataUploadOperation(self):
        print(getDT(), "| REMOTE | Polling local storage...")
        timeSeriesData = self.__storage.getAllTimeSeriesData()
        if len(timeSeriesData) > 0:
            self.runTimeSeriesDataUploadOperation(timeSeriesData)

        timeSeriesImageData = self.__storage.getAllTimeSeriesImageData()
        if len(timeSeriesImageData) > 0:
            self.runTimeSeriesImageDataUploadOperation(timeSeriesImageData)

    def runTimeSeriesDataUploadOperation(self, timeSeriesData):
        print(getDT(), "| REMOTE | Has data to upload...")
        for timeSeriesDatum in timeSeriesData:
            print(getDT(), "| REMOTE | Uploading datum...")

            # Perform our submission of our time-series datum into
            # the remote API web-service.
            msg, wasSuccessful = self.__mikaponicsAPI.postTimeSeriesDatum(
                self.__token,
                timeSeriesDatum.get('instrument_uuid'),
                timeSeriesDatum.get('value'),
                timeSeriesDatum.get('timestamp'),
                timeSeriesDatum.get('timestep')
            )

            # CASE 1 OF 2:
            # CHECK TO SEE IF THE POST WAS SUCCESSFUL TO OUR REMOTE API
            # WEB-SERVICE AND IF SO THEN DO THE FOLLOWING CODE.
            if wasSuccessful:
                print(getDT(), "| REMOTE | Deleting local datum...")
                self.__storage.deleteTimeSeriesDatum(timeSeriesDatum.get('id'))
                print(getDT(), "| REMOTE | Deleted local datum.")

            # CASE 2 OF 2:
            # ELSE IT WAS FOUND OUT THAT THE POST WAS A FAILURE SO WE WILL
            # NEED TO THE FOLLOWING BLOCK OF CODE.
            else:
                # If there is a message, whatever it is, we will make our
                # application just get a new API token to resolve this
                # issue.
                if msg:
                    if "You do not have permission to access this API-endpoint" in msg:
                        print(getDT(), "| REMOTE | Will retry again.")
                    elif "Token needs to refreshed" in msg:
                        print(getDT(), "| REMOTE | Will re-authenticate again...")
                        self.__token = None
                        self.runFetchTokenOperationLoop()

                # Terminate the loop because we have an error and we do not
                # want to iterate through all the data again.
                print(getDT(), "| REMOTE | Terminating loop...")
                break;

    def runTimeSeriesImageDataUploadOperation(self, timeSeriesImageData):
        print(getDT(), "| REMOTE | Has images to upload...")
        for timeSeriesImageDatum in timeSeriesImageData:
            print(getDT(), "| REMOTE | Uploading datum...")

            # DEVELOPERS NOTE:
            # - READ: https://pythonhosted.org/Pyro4/tipstricks.html?highlight=image#binarytransfer
            # - In essence we need to use the `serpent` library to deserialize and convert to binary.
            image_info = timeSeriesImageDatum.get('value')
            image_data = serpent.tobytes(image_info)   # in case of serpent encoded bytes

            # Perform our submission of our time-series datum into
            # the remote API web-service.
            msg, wasSuccessful = self.__mikaponicsAPI.postTimeSeriesImageDatum(
                self.__token,
                timeSeriesImageDatum.get('instrument_uuid'),
                image_data,
                timeSeriesImageDatum.get('timestamp'),
                timeSeriesImageDatum.get('timestep')
            )

            # CASE 1 OF 2:
            # CHECK TO SEE IF THE POST WAS SUCCESSFUL TO OUR REMOTE API
            # WEB-SERVICE AND IF SO THEN DO THE FOLLOWING CODE.
            if wasSuccessful:
                print(getDT(), "| REMOTE | Deleting local image datum...")
                self.__storage.deleteTimeSeriesImageDatum(timeSeriesImageDatum.get('id'))
                print(getDT(), "| REMOTE | Deleted local image datum.")

            # CASE 2 OF 2:
            # ELSE IT WAS FOUND OUT THAT THE POST WAS A FAILURE SO WE WILL
            # NEED TO THE FOLLOWING BLOCK OF CODE.
            else:
                # If there is a message, whatever it is, we will make our
                # application just get a new API token to resolve this
                # issue.
                if msg:
                    if "You do not have permission to access this API-endpoint" in msg:
                        print(getDT(), "| REMOTE | Will retry again.")
                    elif "Token needs to refreshed" in msg:
                        print(getDT(), "| REMOTE | Will re-authenticate again...")
                        self.__token = None
                        self.runFetchTokenOperationLoop()

                # Terminate the loop because we have an error and we do not
                # want to iterate through all the data again.
                print(getDT(), "| REMOTE | Terminating loop...")
                break;

if __name__ == "__main__":
    """
    Main entry into the main program.
    """
    app = RemoteServiceApp()
    app.beginOperation()
    app.runOnMainLoop()
