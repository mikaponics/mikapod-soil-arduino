#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import signal
import time

import Pyro4
import pytz

from foundation import *


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
    print(getDT(), '| LOGGER | Caught signal %d' % signum)
    print("-------------------------------------------------------------------")
    raise ServiceExit


class InstrumentDataLoggerService(object):

    def __init__(self):
        self.__instrument = Pyro4.Proxy("PYRONAME:mikapod.instrument")
        self.__storage = Pyro4.Proxy("PYRONAME:mikapod.storage")
        self.__cycle_start_dt = getDT()

    def runOnMainLoop(self):
        """
        Function is the main loop of the application.
        """
        print(getDT(), "| LOGGER | Register the signal handlers.")
        signal.signal(signal.SIGTERM, onServiceShutdownHandler)
        signal.signal(signal.SIGINT, onServiceShutdownHandler)

        print(getDT(), "| LOGGER | Starting main program.")

        try:
            while True:
                self.runOperationLoop()
                time.sleep(1)
        except ServiceExit:
            print(getDT(), "| LOGGER | Gracefully shutting down.")
        print(getDT(), "| LOGGER | Exiting main program.")

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
        print(current_cycle_dt, "| LOGGER | Duration:", duration)
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
        readings = self.__instrument.getData()

        # Defensive Code: If nothing was returned then we must stop and error.
        if readings is None:
            print(current_cycle_dt, "| LOGGER | Error: No data returned from external device.")
            exit()

        # Extract the data.
        humidity = readings['humidity']
        temperature_primary = readings['temperature_primary']
        temperature_secondary = readings['temperature_secondary']
        illuminance = readings['illuminance']
        pressure = readings['pressure']
        altitude = readings['altitude']
        soil_moisture = readings['soil_moisture']

        # Process our values.
        self.processHumidity(humidity, now_ts)
        self.processTemperature(temperature_primary, temperature_secondary, now_ts)
        self.processIlluminance(illuminance, now_ts)
        self.processPressure(pressure, now_ts)
        self.processAltitude(altitude, now_ts)
        self.processSoilMoisture(soil_moisture, now_ts)

    def processHumidity(self, humidity, now_ts):
        # CASE 1 OF 2: An error occured when attempting to make a reading.
        if humidity['status'] == 0:
            print(getDT(), "| LOGGER | HUMIDITY | Error:", humidity['error'])
            return

        # SELF 2 OF 2: No errors occured when attempting to make a reading.
        humidity_value = humidity['value']
        self.__storage.insertTimeSeriesDatum(
            HUMIDITY_INSTRUMENT_UUID,
            float(humidity_value),
            now_ts,
            TIME_STEP
        )
        print(getDT(), "| LOGGER | HUMIDITY | Value:", humidity_value)
        print(getDT(), "| LOGGER | HUMIDITY | Timestamp:", now_ts)

    def processTemperature(self, temperature_primary, temperature_secondary, now_ts):
        # CASE 1 OF 2: An error occured when attempting to make a reading.
        if temperature_primary['status'] == 0 or temperature_secondary['status'] == 0:
            print(getDT(), "| LOGGER | TEMPERATURE PRIMARY | Error:", temperature_primary['error'])
            print(getDT(), "| LOGGER | TEMPERATURE SECONDARY | Error:", temperature_secondary['error'])
            return

        # SELF 2 OF 2: No errors occured when attempting to make a reading.
        temperature_value_1 = temperature_primary['value']
        temperature_value_2 = temperature_secondary['value']
        temperature_value_avg = (temperature_value_1+temperature_value_2) / 2.0

        self.__storage.insertTimeSeriesDatum(
            TEMPERATURE_INSTRUMENT_UUID,
            float(temperature_value_avg),
            now_ts,
            TIME_STEP
        )
        print(getDT(), "| LOGGER | TEMPERATURE | AVG Value:", temperature_value_avg)
        print(getDT(), "| LOGGER | TEMPERATURE | Timestamp:", now_ts)

    def processIlluminance(self, illuminance, now_ts):
        # CASE 1 OF 2: An error occured when attempting to make a reading.
        if illuminance['status'] == 0:
            print(getDT(), "| LOGGER | ILLUMINANCE | Error:", illuminance['error'])
            return

        # SELF 2 OF 2: No errors occured when attempting to make a reading.
        illuminance_value = illuminance['value']
        self.__storage.insertTimeSeriesDatum(
            ILLUMINANCE_INSTRUMENT_UUID,
            float(illuminance_value),
            now_ts,
            TIME_STEP
        )
        print(getDT(), "| LOGGER | ILLUMINANCE | Value:", illuminance_value)
        print(getDT(), "| LOGGER | ILLUMINANCE | Timestamp:", now_ts)

    def processPressure(self, pressure, now_ts):
        # CASE 1 OF 2: An error occured when attempting to make a reading.
        if pressure['status'] == 0:
            print(getDT(), "| LOGGER | PRESSURE | Error:", pressure['error'])
            return

        # SELF 2 OF 2: No errors occured when attempting to make a reading.
        pressure_value = pressure['value']
        self.__storage.insertTimeSeriesDatum(
            PRESSURE_INSTRUMENT_UUID,
            float(pressure_value),
            now_ts,
            TIME_STEP
        )
        print(getDT(), "| LOGGER | PRESSURE | Value:", pressure_value)
        print(getDT(), "| LOGGER | PRESSURE | Timestamp:", now_ts)

    def processAltitude(self, altitude, now_ts):
        # CASE 1 OF 2: An error occured when attempting to make a reading.
        if altitude['status'] == 0:
            print(getDT(), "| LOGGER | ALTITUDE | Error:", altitude['error'])
            return

        # SELF 2 OF 2: No errors occured when attempting to make a reading.
        altitude_value = altitude['value']
        self.__storage.insertTimeSeriesDatum(
            ALTITUDE_INSTRUMENT_UUID,
            float(altitude_value),
            now_ts,
            TIME_STEP
        )
        print(getDT(), "| LOGGER | ALTITUDE | Value:", altitude_value)
        print(getDT(), "| LOGGER | ALTITUDE | Timestamp:", now_ts)

    def processSoilMoisture(self, soil, now_ts):
        # CASE 1 OF 2: An error occured when attempting to make a reading.
        if soil['status'] == 0:
            print(getDT(), "| LOGGER | SOIL MOISTURE | Error:", soil['error'])
            return

        # SELF 2 OF 2: No errors occured when attempting to make a reading.
        soil_value = soil['value']
        self.__storage.insertTimeSeriesDatum(
            SOIL_MOISTURE_INSTRUMENT_UUID,
            float(soil_value),
            now_ts,
            TIME_STEP
        )
        print(getDT(), "| LOGGER | SOIL MOISTURE | Value:", soil_value)
        print(getDT(), "| LOGGER | SOIL MOISTURE | Timestamp:", now_ts)

if __name__ == "__main__":
    """
    Main entry into the main program.
    """
    app = InstrumentDataLoggerService()
    app.runOnMainLoop()
