#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import signal
import time
from random import randrange

import Pyro4
import pytz

from foundation import *


"""
************************
DO NOT RUN IN PRODUCTION
************************
Application used populate the database with FAKE data (aka made up). This
application is useful for the `remote_service` when testing submissions to the
API endpoint.
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
    print(getDT(), '| FAKE LOGGER | Caught signal %d' % signum)
    print("-------------------------------------------------------------------")
    raise ServiceExit


class FakeInstrumentDataLoggerService(object):

    def __init__(self):
        self.__storage = Pyro4.Proxy("PYRONAME:mikapod.storage")
        self.__cycle_start_dt = getDT()

    def runOnMainLoop(self):
        """
        Function is the main loop of the application.
        """
        print(getDT(), "| FAKE LOGGER | Register the signal handlers.")
        signal.signal(signal.SIGTERM, onServiceShutdownHandler)
        signal.signal(signal.SIGINT, onServiceShutdownHandler)

        print(getDT(), "| FAKE LOGGER | Starting main program.")

        try:
            while True:
                self.runOperationLoop()
                time.sleep(1)
        except ServiceExit:
            print(getDT(), "| FAKE LOGGER | Gracefully shutting down.")
        print(getDT(), "| FAKE LOGGER | Exiting main program.")

    def runOperationLoop(self):
        # Keep running the main runtime loop with various
        # being inputted for a frame of reference in the computations
        # along with a few computations.
        while True:
            current_cycle_dt = getDT()
            duration = current_cycle_dt - self.__cycle_start_dt
            now_ts = int(time.time())
            self.runOperation(current_cycle_dt, duration, now_ts)
            time.sleep(1)

    def runOperation(self, current_cycle_dt, duration, now_ts):
        """
        Function will check to see if the current datetime has "minutes" equal
        to the target minutes AND OR the duration of a cycle elapsed. If any
        of these conditions are met then we run the action.
        """
        print(current_cycle_dt, "| FAKE LOGGER | Tick at duration:", duration)
        # self.runAction(current_cycle_dt, now_ts) # DEBUGGING PURPOSES ONLY.

        if current_cycle_dt.second == 0:
            if current_cycle_dt.minute % TIME_STEP_IN_MINUTES == 0 or current_cycle_dt.minute == 0:
                self.runAction(current_cycle_dt, now_ts)
                self.__cycle_start_dt = getDT()

            elif duration > TARGET_RUNTIME_CYCLE_DURATION:
                self.runAction(current_cycle_dt, now_ts)
                self.__cycle_start_dt = getDT()

    def runAction(self, current_cycle_dt, now_ts):
        # Make RPC call to our `instrument service` to fetch our latest
        # data from the external device (Arduino).
        readings = {
            'humidity': {
                'status': 1,
                'value': randrange(100),
            },
            'temperature': {
                'status': 1,
                'value': randrange(40),

            },
            'illuminance': {
                'status': 1,
                'value': randrange(1000),
            },
            'pressure': {
                'status': 1,
                'value': randrange(500),
            }
        }

        # Defensive Code: If nothing was returned then we must stop and error.
        if readings is None:
            print(current_cycle_dt, "| FAKE LOGGER | Error: No data returned from external device.")
            exit()

        # Extract the data.
        humidity = readings['humidity']
        temperature = readings['temperature']
        illuminance = readings['illuminance']
        pressure = readings['pressure']

        # Process our values.
        self.processHumidity(humidity, now_ts)
        self.processTemperature(temperature, now_ts)
        self.processIlluminance(illuminance, now_ts)
        self.processPressure(pressure, now_ts)

    def processHumidity(self, humidity, now_ts):
        # CASE 1 OF 2: An error occured when attempting to make a reading.
        if humidity['status'] == 0:
            print(getDT(), "| FAKE LOGGER | HUMIDITY | Error:", humidity['error'])
            return

        # SELF 2 OF 2: No errors occured when attempting to make a reading.
        humidity_value = humidity['value']
        self.__storage.insertTimeSeriesDatum(
            HUMIDITY_INSTRUMENT_UUID,
            float(humidity_value),
            now_ts,
            TIME_STEP
        )
        print(getDT(), "| FAKE LOGGER | HUMIDITY | Value:", humidity_value)
        print(getDT(), "| FAKE LOGGER | HUMIDITY | Timestamp:", now_ts)

    def processTemperature(self, temperature, now_ts):
        # CASE 1 OF 2: An error occured when attempting to make a reading.
        if temperature['status'] == 0:
            print(getDT(), "| FAKE LOGGER | TEMPERATURE | Error:", temperature['error'])
            return

        # SELF 2 OF 2: No errors occured when attempting to make a reading.
        temperature_value = temperature['value']
        self.__storage.insertTimeSeriesDatum(
            TEMPERATURE_INSTRUMENT_UUID,
            float(temperature_value),
            now_ts,
            TIME_STEP
        )
        print(getDT(), "| FAKE LOGGER | TEMPERATURE | Value:", temperature_value)
        print(getDT(), "| FAKE LOGGER | TEMPERATURE | Timestamp:", now_ts)

    def processIlluminance(self, illuminance, now_ts):
        # CASE 1 OF 2: An error occured when attempting to make a reading.
        if illuminance['status'] == 0:
            print(getDT(), "| FAKE LOGGER | ILLUMINANCE | Error:", illuminance['error'])
            return

        # SELF 2 OF 2: No errors occured when attempting to make a reading.
        illuminance_value = illuminance['value']
        self.__storage.insertTimeSeriesDatum(
            ILLUMINANCE_INSTRUMENT_UUID,
            float(illuminance_value),
            now_ts,
            TIME_STEP
        )
        print(getDT(), "| FAKE LOGGER | ILLUMINANCE | Value:", illuminance_value)
        print(getDT(), "| FAKE LOGGER | ILLUMINANCE | Timestamp:", now_ts)

    def processPressure(self, pressure, now_ts):
        # CASE 1 OF 2: An error occured when attempting to make a reading.
        if pressure['status'] == 0:
            print(getDT(), "| FAKE LOGGER | PRESSURE | Error:", pressure['error'])
            return

        # SELF 2 OF 2: No errors occured when attempting to make a reading.
        pressure_value = pressure['value']
        self.__storage.insertTimeSeriesDatum(
            PRESSURE_INSTRUMENT_UUID,
            float(pressure_value),
            now_ts,
            TIME_STEP
        )
        print(getDT(), "| FAKE LOGGER | PRESSURE | Value:", pressure_value)
        print(getDT(), "| FAKE LOGGER | PRESSURE | Timestamp:", now_ts)


if __name__ == "__main__":
    """
    Main entry into the main program.
    """
    app = FakeInstrumentDataLoggerService()
    app.runOnMainLoop()
