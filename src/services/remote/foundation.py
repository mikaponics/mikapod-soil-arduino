#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import os

import pytz
from dotenv import load_dotenv
load_dotenv(verbose=True)


#------------------------------------------------------------------------------#
#                          APPLICATION CONFIGURATION                           #
#------------------------------------------------------------------------------#

# API WEB-SERVICE CONFIGURATION
WEB_SERVICE_URL = os.getenv("WEB_SERVICE_URL")
WEB_SERVICE_CLIENT_ID = os.getenv("WEB_SERVICE_CLIENT_ID")
WEB_SERVICE_CLIENT_SECRET = os.getenv("WEB_SERVICE_CLIENT_SECRET")
WEB_SERVICE_DEVICE_UUID = os.getenv("WEB_SERVICE_DEVICE_UUID")

# APPLICATION CONFIGURATION
LOCAL_TIMEZONE = pytz.timezone(os.getenv("LOCAL_TIMEZONE_NAME"))


#------------------------------------------------------------------------------#
#                                  CONSTANTS                                   #
#------------------------------------------------------------------------------#
ACCESS_TOKEN_KEY = 'APIToken'


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
