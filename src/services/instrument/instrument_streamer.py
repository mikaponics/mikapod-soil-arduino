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


"""
THE PURPOSE OF THIS CODE IS TO PROVIDE A STREAM OF DATA FROM THE INSTRUMENTS
TO THE PROGRAMMERS CONSOLE TO SEE WHAT THE ARDUINO DEVICE IS RETURNING. THIS
CODE IS TO BE USED FOR TESTING PURPOSES ONLY! **DO NOT USE IN PRODUCTION**
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
    print(getDT(), '| INSTRUMENT STREAM | Caught signal %d' % signum)
    print("-------------------------------------------------------------------")
    raise ServiceExit


class InstrumentPrint(object):
    """
    Service interacts with the external device (Arduino) and prints the data
    on a specific interval to the user's console.
    """

    def __init__(self):
        '''
        Wait until our computer can connect to the external device (Ardunio)
        over serial USB communication to begin running our program.
        '''
        try:
            self.__serial = Serial(SERIAL_PORT, SERIAL_BAUD, timeout=SERIAL_TIMEOUT)
            time.sleep(2) # Wait for Arduino to become connected with our application.
            print(getDT(), "| INSTRUMENT STREAM | Successfully connected to external device on serial port:", SERIAL_PORT);
        except Exception as e:
            if "could not open port" in str(e):
                print(getDT(), "| INSTRUMENT STREAM | Could not connect to external device on serial port:", SERIAL_PORT);
                exit()

        '''
        Load up our application variables.
        '''
        self.__storage = Pyro4.Proxy("PYRONAME:mikapod.storage")
        self.__cycle_start_dt = getDT()

    def runOnMainLoop(self):
        """
        Function is the main loop of the application.
        """
        print(getDT(), "| INSTRUMENT STREAM | Register the signal handlers.")
        signal.signal(signal.SIGTERM, onServiceShutdownHandler)
        signal.signal(signal.SIGINT, onServiceShutdownHandler)

        print(getDT(), "| INSTRUMENT STREAM | Starting main program.")
        try:
            self.runInitializationLoop()
            self.runOperationLoop()
        except ServiceExit:
            print(getDT(), "| INSTRUMENT STREAM | Gracefully shutting down.")
        print(getDT(), "| INSTRUMENT STREAM | Exiting main program.")

    def runInitializationLoop(self):
        '''
        Function will consume the main runtime loop and block it until the
        external device (Arduino) has warmed up and is ready to be used.
        '''
        print(getDT(), "| INSTRUMENT STREAM | Warming up external device...")
        while True:
            byte_data = self.__serial.readline()

             # https://stackoverflow.com/questions/6269765/what-does-the-b-character-do-in-front-of-a-string-literal#6273618
            json_string = byte_data.decode('UTF-8')

            if len(json_string) > 0:
                if "READY" in str(json_string):
                    print(getDT(), "| INSTRUMENT STREAM | External device is ready.")
                    parsed = json.loads(json_string) # FOR DEBUGGING PURPOSES ONLY.
                    print(getDT(), "| INSTRUMENT STREAM | External device output:\n", json.dumps(parsed, indent=4, sort_keys=True))
                    break
            time.sleep(1)

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
        print(current_cycle_dt, "| INSTRUMENT STREAM | Duration:", duration)
        if current_cycle_dt.second == 0:
            if current_cycle_dt.minute % TIME_STEP_IN_MINUTES == 0 or current_cycle_dt.minute == 0:
                self.runAction(current_cycle_dt, now_ts)
                self.__cycle_start_dt = getDT()

            elif duration > TARGET_RUNTIME_CYCLE_DURATION:
                self.runAction(current_cycle_dt, now_ts)
                self.__cycle_start_dt = getDT()

    def runAction(self, current_cycle_dt, now_ts):
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
            parsed = json.loads(json_string)
            print(getDT(), "| INSTRUMENT STREAM | Output:\n", json.dumps(parsed, indent=4, sort_keys=True))


if __name__ == "__main__":
    """
    Main entry into the main program.
    """
    app = InstrumentPrint()
    app.runOnMainLoop()
