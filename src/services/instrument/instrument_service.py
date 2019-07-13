#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import signal
import time
import json

from serial import Serial
import Pyro4
import pytz

from foundation import *
from instrument_dao import InstrumentDataAccessObject


"""
Application used to interface with the hardware instruments (ex: humidity,
temperature, etc) and continously save the latest data.
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
    print(getDT(), '| INSTRUMENT | Caught signal %d' % signum)
    print("-------------------------------------------------------------------")
    raise ServiceExit


@Pyro4.expose
class Instrumentation(object):
    """
    Class which will be the distributed object used to make remote method calls.
    """

    def __init__(self):
        """
        Constructor function used to setup our singleton class.
        """
        self.__instrumentDAO = InstrumentDataAccessObject.getInstance()

    def getData(self):
        """
        Function will get data for all the instruments on the external device.
        """
        data = self.__instrumentDAO.getData()
        return data


class InstrumentationService(object):
    """
    Service which provides access to the external device (Arduino) for other
    services to accesss using RPC calls.
    """

    def __init__(self):
        # DEVELOPERS NOTE:
        # Initialize our singleton instance so when RPC calls are made
        # then the device will be ready and waiting to take calls.
        InstrumentDataAccessObject.getInstance()

    def runOnMainLoop(self):
        """
        Function is the main loop of the application.
        """
        print(getDT(), "| INSTRUMENT | Register the signal handlers.")
        signal.signal(signal.SIGTERM, onServiceShutdownHandler)
        signal.signal(signal.SIGINT, onServiceShutdownHandler)

        print(getDT(), "| INSTRUMENT | Starting service.")

        try:
            daemon = Pyro4.Daemon()                       # make a Pyro daemon
            ns = Pyro4.locateNS()                         # find the name server
            uri = daemon.register(Instrumentation)        # register the greeting maker as a Pyro object
            ns.register("mikapod.instrument", uri)        # register the object with a name in the name server

            print(getDT(), "| INSTRUMENT | Ready.")
            daemon.requestLoop()                   # start the event loop of the server to wait for calls

        except ServiceExit:
            print(getDT(), "| INSTRUMENT | Gracefully shutting down.")
        print(getDT(), "| INSTRUMENT | Exiting main program.")

if __name__ == "__main__":
    """
    Main entry into the main program.
    """
    app = InstrumentationService()
    app.runOnMainLoop()
