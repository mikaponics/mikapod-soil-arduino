#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import json

import requests
import msgpack
from oauthlib.oauth2 import BackendApplicationClient
from requests.auth import HTTPBasicAuth
from oauthlib.oauth2 import TokenExpiredError
from requests_oauthlib import OAuth2Session

from foundation import *

# DEVELOPERS NOTE: We are disabling SSL so we can test but when we run
# in production the URL will point to a secure link.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


class MikaponicsAPI:
    """
    Singleton class used to provide a single point of access with our local
    persistent storage with the application.
    """
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if MikaponicsAPI.__instance == None:
            MikaponicsAPI()
        return MikaponicsAPI.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if MikaponicsAPI.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            MikaponicsAPI.__instance = self
            MikaponicsAPI.__updateTokenFunc = None

    def beginOperation(self, onTokenRefreshedHandler):
        self.__updateTokenFunc = onTokenRefreshedHandler

    def terminateOperation(self):
        pass

    def getAPIToken(self):
        try:
            # Fetch our latest token.
            print(getDT(), "| API | Beginning to fetch API Token")
            client = BackendApplicationClient(client_id=WEB_SERVICE_CLIENT_ID)
            oauth = OAuth2Session(client=client)
            token = oauth.fetch_token(
               token_url=WEB_SERVICE_URL + "/o/token/",
               client_id=WEB_SERVICE_CLIENT_ID,
               client_secret=WEB_SERVICE_CLIENT_SECRET
            )

            # For debugging purposes only.
            print(getDT(), "| API | Token received.")
            print(getDT(), "| API | Response:", json.dumps(token, indent=4))

            # Return our values.
            return token, True
        except requests.ConnectionError:
            print(getDT(), "| API | No internet connection available.")
        except Exception as e:
            if "invalid_client" in str(e):
                print(getDT(), "| API | Wrong oauth credentials.")
            else:
                print(getDT(), "| API | Exception:", str(e))
        return None, False

    def postTimeSeriesDatum(self, token, instrumentUUID, value, timestamp, time_step):
        try:
            print(getDT(), "| API | Posting time-series data to remote API web-service...")
            print(getDT(), "| API |", instrumentUUID, value, timestamp)

            refresh_url = WEB_SERVICE_URL + "/o/token/"
            extra = {
                'client_id': WEB_SERVICE_CLIENT_ID,
                'client_secret': WEB_SERVICE_CLIENT_SECRET
            }
            client = OAuth2Session(WEB_SERVICE_CLIENT_ID,token=token)
            protected_url = WEB_SERVICE_URL + "/api/data"
            json_data = {
                'instrument_uuid': str(instrumentUUID),
                'value': value,
                'unix_timestamp': str(timestamp),
                'time_step': time_step
            }

            # SERIALIZE OUR JSON DATA INTO `MESSAGE PACK` SO WE CAN SEND
            # MORE DATA MORE EFFICIENTLY.
            buffer = msgpack.packb(json_data, use_bin_type=True)

            # Perform our submission with our oAuth 2.0 credentials.
            try:
                r = client.post(
                    protected_url,
                    timeout=5,
                    data=buffer,
                    headers={
                        'Content-Type': 'application/msgpack;', # USE `MESSAGE PACK` ENCODING WITH OUR API SERVER.
                        'Accept': 'application/msgpack',
                    }
                )
            except TokenExpiredError as e:
                print(getDT(), "| API |", str(e))
                return "Token needs to refreshed", False

            # Handle our response.
            if r.status_code == requests.codes.created:
                # DESERIALIZE OUR `MESSAGE PACK` DATA FROM THE SERVER INTO
                # `JSON` FORMAT WHICH IS EASIER TO READ FOR PYTHON.
                data = msgpack.unpackb(r.content, raw=False)
                print(getDT(), "| API | Submission was a success.")
                print(getDT(), "| API | Response:", data)
                return data, True
            else:
                print(getDT(), "| API | Submission was a failure.")
                print(getDT(), "| API | Response:", str(r.text))
                return str(r.text), False
        except requests.ConnectionError:
            print(getDT(), "| API | No internet connection available.")
        return None, False

    def postTimeSeriesImageDatum(self, token, instrumentUUID, byte_content, timestamp, time_step):
        try:
            # https://stackoverflow.com/a/37239382
            import base64
            base64_bytes = base64.b64encode(byte_content)
            base64_string = base64_bytes.decode("utf-8")

            print(getDT(), "| API | Posting time-series image data to remote API web-service...")
            # print(getDT(), "| API |", instrumentUUID, value, timestamp) #TOO BIG TO PRINT

            refresh_url = WEB_SERVICE_URL + "/o/token/"
            extra = {
                'client_id': WEB_SERVICE_CLIENT_ID,
                'client_secret': WEB_SERVICE_CLIENT_SECRET
            }
            client = OAuth2Session(WEB_SERVICE_CLIENT_ID,token=token)
            protected_url = WEB_SERVICE_URL + "/api/image-data"
            json_data = {
                'instrument_uuid': instrumentUUID,
                'value': base64_string,
                'unix_timestamp': str(timestamp),
                'time_step': time_step
            }

            #TODO: SERIALIZE TO MESSAGE PACK FORMAT.

            # Perform our submission with our oAuth 2.0 credentials.
            try:
                r = client.post(
                    protected_url,
                    timeout=5,
                    json=json_data
                )
            except TokenExpiredError as e:
                print(getDT(), "| API |", str(e))
                return "Token needs to refreshed", False

            except Exception as e:
                print(getDT(), "| API | Exception with error:", str(e))
                return "Exception detected", False

            # Handle our response.
            if r.status_code == requests.codes.created:
                #TODO: DESERIALIZE TO MESSAGE PACK FORMAT.
                print(getDT(), "| API | Submission was a success.")
                print(getDT(), "| API | Response:", json.dumps(r.json(), indent=4))
                return r.json(), True
            else:
                print(getDT(), "| API | Submission was a failure.")
                print(getDT(), "| API | Response:", str(r.text))
                return str(r.text), False
        except requests.ConnectionError:
            print(getDT(), "| API | No internet connection available.")
        return None, False
