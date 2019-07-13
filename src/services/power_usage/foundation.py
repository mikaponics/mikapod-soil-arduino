#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
from datetime import timedelta
import os
import time

import pytz
from dotenv import load_dotenv
load_dotenv(verbose=True)


#------------------------------------------------------------------------------#
#                          APPLICATION CONFIGURATION                           #
#------------------------------------------------------------------------------#

"""
The UUID assigned by Mikaponics for this power-usage instrument.
"""
POWER_USAGE_INSTRUMENT_UUID = os.getenv("POWER_USAGE_INSTRUMENT_UUID")

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
Variable controls what wattage we are to represent for our time-step.
"""
DEVICE_POWER_USAGE_IN_WATTS_PER_TIME_STEP = float(os.getenv("DEVICE_POWER_USAGE_IN_WATTS_PER_TIME_STEP"))


#------------------------------------------------------------------------------#
#                                  CONSTANTS                                   #
#------------------------------------------------------------------------------#

"""
These constants are the values the API service will return and must match
exact value. These values will always be the exact values found in the links
provided in the class descriptions.
"""

class INSTRUMENT_TYPE:
    """
    https://github.com/mikaponics/mikaponics-django/blob/master/mikaponics/foundation/models/instrument.py
    """
    POWER_USAGE = 9


#------------------------------------------------------------------------------#
#                               UTILITY FUNCTIONS                              #
#------------------------------------------------------------------------------#

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
