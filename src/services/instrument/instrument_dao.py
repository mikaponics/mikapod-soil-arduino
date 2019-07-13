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


class InstrumentDataAccessObject:
    """
    Class is a hardware interface over the external device (Arduino).
    """
    # Here will be the instance stored.
    __instance = None
    __is_running = False
    __serial = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if InstrumentDataAccessObject.__instance == None:
            InstrumentDataAccessObject()
        return InstrumentDataAccessObject.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if InstrumentDataAccessObject.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            InstrumentDataAccessObject.__instance = self

            '''
            Wait until our computer can connect to the external device (Ardunio)
            over serial USB communication to begin running our program.
            '''
            try:
                self.__serial = Serial(SERIAL_PORT, SERIAL_BAUD, timeout=SERIAL_TIMEOUT)
                time.sleep(2) # Wait for Arduino to become connected with our application.
                print(getDT(), "| INSTRUMENT DAO | Successfully connected to external device on serial port:", SERIAL_PORT);
            except Exception as e:
                if "could not open port" in str(e):
                    print(getDT(), "| INSTRUMENT DAO | Could not connect to external device on serial port:", SERIAL_PORT);
                    exit()

            '''
            Once connection was established over serial USB, wait until
            the external device warms up and is ready to be used.
            '''
            self.runInitializationLoop()
            return

    def runInitializationLoop(self):
        '''
        Function will consume the main runtime loop and block it until the
        external device (Arduino) has warmed up and is ready to be used.
        '''
        print(getDT(), "| INSTRUMENT DAO | Warming up external device...")
        while True:
            byte_data = self.__serial.readline()

             # https://stackoverflow.com/questions/6269765/what-does-the-b-character-do-in-front-of-a-string-literal#6273618
            json_string = byte_data.decode('UTF-8')

            if len(json_string) > 0:
                if "READY" in str(json_string):
                    print(getDT(), "| INSTRUMENT DAO | External device is ready.")
                    parsed = json.loads(json_string) # FOR DEBUGGING PURPOSES ONLY.
                    print(getDT(), "| INSTRUMENT DAO | External device output:\n", json.dumps(parsed, indent=4, sort_keys=True))
                    self.__is_running = True
                    break
            time.sleep(1)


    def getData(self):
        # DEVELOPERS NOTE:
        # (1) The external device (Arduino) is setup to standby idle until it
        #     receives a poll request from this code, once a poll request has
        #     been submitted then all the sensors get polled and their data is
        #     returned.
        # (2) Please look at the following code to understand how the external
        #     device works in:
        #     src/instruments/mikapod-soil-arduino/mikapod-soil-arduino.ino
        # (3) The reason for design is as follows:
        #     (a) The external device does not have a real-time clock
        #     (b) We don't want to add any real-time clock shields because
        #         extra hardware means it costs more.
        #     (c) We don't want to write complicated code of synching time
        #         from this code because it will make the code complicated.
        #     (d) Therefore we chose to make sensor polling be event based
        #         and this code needs to send a "poll request".

        # STEP 1:
        # We need to send a single byte to the external device (Arduino) which
        # will trigger a polling event on all the sensors.
        self.__serial.write(RX_BYTE)

        # STEP 2:
        # The external device will poll the device, we need to make our main
        # runtime loop to be blocked so we wait until the device finishes and
        # returns all the sensor measurements.
        byte_data = self.__serial.readline()
        json_string = byte_data.decode('UTF-8') # NOTE: https://stackoverflow.com/questions/6269765/what-does-the-b-character-do-in-front-of-a-string-literal#6273618

        # STEP 3:
        # Check to see if ANY data was returned from the external device, if
        # there was then we load up the string into a JSON object.
        if len(json_string) > 0:
            return json.loads(json_string)
        return None
