#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
from datetime import timedelta
import os
import time

import pytz
from dotenv import load_dotenv
load_dotenv(verbose=True)


#---------------------------#
# APPLICATION CONFIGURATION #
#---------------------------#

"""
Variables used for configuring the how the serial USB communication will be
handled with the Arduino device.
"""
SERIAL_PORT = os.getenv("SERIAL_PORT")
SERIAL_BAUD = int(os.getenv("SERIAL_BAUD"))
SERIAL_TIMEOUT = int(os.getenv("SERIAL_TIMEOUT"))


"""
Variable controls what timezone formatting we must apply to our UTC datetimes.
"""
LOCAL_TIMEZONE = pytz.timezone(os.getenv("LOCAL_TIMEZONE_NAME"))


"""
Variable controls when the readings will be taken. For example if we have a
value of "1" then the times of recording will be: 1:01 AM, 1:02 AM, 1:03 AM, etc.
For example if we have a value of "5" then the time of recording will be:
1:05 AM, 1:10 AM, 1:15 AM, etc. We refer to this variable as a "time-step"
and we measure it in per minute intervals.
"""
TIME_STEP_IN_MINUTES = int(os.getenv("TIME_STEP_IN_MINUTES"))
TIME_STEP = os.getenv("TIME_STEP")


"""
The time-step translated into a python `timedelta` object.
"""
TARGET_RUNTIME_CYCLE_DURATION = timedelta(minutes=int(os.getenv("TIME_STEP_IN_MINUTES")))


"""
The UUID values assigned by the API web-service to our IoT instruments.
"""
HUMIDITY_INSTRUMENT_UUID = os.getenv("HUMIDITY_INSTRUMENT_UUID")
TEMPERATURE_INSTRUMENT_UUID = os.getenv("TEMPERATURE_INSTRUMENT_UUID")
ILLUMINANCE_INSTRUMENT_UUID = os.getenv("ILLUMINANCE_INSTRUMENT_UUID")
PRESSURE_INSTRUMENT_UUID = os.getenv("PRESSURE_INSTRUMENT_UUID")
POWER_USAGE_UUID = os.getenv("POWER_USAGE_UUID")
ALTITUDE_INSTRUMENT_UUID = os.getenv("ALTITUDE_INSTRUMENT_UUID")
SOIL_MOISTURE_INSTRUMENT_UUID = os.getenv("SOIL_MOISTURE_INSTRUMENT_UUID")


#------------------#
# GLOBAL CONSTANTS #
#------------------#

"""
Simple variable used to send to the Arduino device.
"""
RX_BYTE = '1'.encode('UTF-8')


"""
These constants are the values the API service will return and must match
exact value. These values will always be the exact values found in the links
provided in the class descriptions.
"""

class INSTRUMENT_TYPE:
    """
    https://github.com/mikaponics/mikaponics-back/blob/master/mikaponics/foundation/models/instrument.py
    """
    HUMIDITY = 1
    AIR_TEMPERATURE = 2
    AIR_PRESSURE = 6
    ILLUMINANCE = 17
    SOIL_MOISTURE = 18


#-------------------#
# UTILITY FUNCTIONS #
#-------------------#

def getDT():
    """
    Function will return the current datetime aware of the local timezone.
    """
    # Get our UTC datetime without any timezone awareness.
    naive_now_dt = datetime.datetime.utcnow()

    # Convert to our local timezone.
    utc_aware_now_dt = naive_now_dt.replace(tzinfo=pytz.utc) # Make UTC timezone aware.
    local_aware_now_dt = utc_aware_now_dt.astimezone(LOCAL_TIMEZONE) # Convert to local timezone.

    # Return our datetime converted to our local timezone.
    return local_aware_now_dt
