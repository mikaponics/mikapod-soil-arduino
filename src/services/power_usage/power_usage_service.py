#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import signal
import time

import Pyro4
import pytz

from foundation import *


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
    print(getDT(), '| POWER USAGE | Caught signal %d' % signum)
    print("-------------------------------------------------------------------")
    raise ServiceExit


class PowerUsageLoggingService(object):

    def __init__(self):
        print(getDT(), "| POWER USAGE | Starting service.")
        self.__storage = Pyro4.Proxy("PYRONAME:mikapod.storage")
        self.__cycle_start_dt = self.get_local_dt()
        print(getDT(), "| POWER USAGE | Ready.")

    def get_local_dt(self):
        naive_now_dt = datetime.datetime.utcnow()
        utc_aware_now_dt = naive_now_dt.replace(tzinfo=pytz.utc) # Make UTC timezone aware.
        local_aware_now_dt = utc_aware_now_dt.astimezone(LOCAL_TIMEZONE) # Convert to local timezone.
        return local_aware_now_dt

    def runOnMainLoop(self):
        """
        Function is the main loop of the application.
        """
        print(getDT(), "| POWER USAGE | Register the signal handlers.")
        signal.signal(signal.SIGTERM, onServiceShutdownHandler)
        signal.signal(signal.SIGINT, onServiceShutdownHandler)

        try:
            # Keep running the main runtime loop with the `start_dt`
            # being inputted for a frame of reference in the computations.
            while True:
                self.runOperationLoop()
                time.sleep(1)

        except ServiceExit:
            print(getDT(), "| POWER USAGE | Gracefully shutting down.")
        print(getDT(), "| POWER USAGE | Exiting main program.")

    def runOperationLoop(self):
        """
        Function will check to see if the current datetime has "minutes" equal
        to the target minutes AND OR the duration of a cycle elapsed. If any
        of these conditions are met then we run the action.
        """
        current_cycle_dt = self.get_local_dt()
        duration = current_cycle_dt - self.__cycle_start_dt
        now_ts = int(time.time())

        print(getDT(), "| POWER USAGE | Duration:", duration)
        if current_cycle_dt.second == 0:
            if current_cycle_dt.minute % TIME_STEP_IN_MINUTES == 0 or current_cycle_dt.minute == 0:
                self.runAction(current_cycle_dt, now_ts)
                self.__cycle_start_dt = self.get_local_dt()

            elif duration > TARGET_RUNTIME_CYCLE_DURATION:
                self.runAction(current_cycle_dt, now_ts)
                self.__cycle_start_dt = self.get_local_dt()

    def runAction(self, current_cycle_dt, now_ts):
        self.__storage.insertTimeSeriesDatum(
            POWER_USAGE_INSTRUMENT_UUID,
            DEVICE_POWER_USAGE_IN_WATTS_PER_TIME_STEP,
            now_ts,
            TIME_STEP
        )
        print(
            getDT(), "| POWER USAGE | Used", DEVICE_POWER_USAGE_IN_WATTS_PER_TIME_STEP, "Watts from", str(self.__cycle_start_dt), "to", str(current_cycle_dt)
        )

if __name__ == "__main__":
    """
    Main entry into the main program.
    """
    app = PowerUsageLoggingService()
    app.runOnMainLoop()
