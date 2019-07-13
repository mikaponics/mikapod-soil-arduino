#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import os

import pytz
from dotenv import load_dotenv
load_dotenv(verbose=True)


#---------------------------#
# APPLICATION CONFIGURATION #
#---------------------------#

DATABASE = os.getenv("DATABASE")
LOCAL_TIMEZONE = pytz.timezone(os.getenv("LOCAL_TIMEZONE_NAME"))


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
