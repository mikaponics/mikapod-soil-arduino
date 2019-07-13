#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import time
from peewee import *

from foundation import *


"""
The following code will provide an interface with the local persistent storage
singleton class. The storage will be used to store time-series data in a SQL
database using the``peewee`` library. The application will call this interface
to store, list, retrieve and delete time-series data which we have locally.
"""


# create a peewee database instance -- our models will use this database to
# persist information

database = SqliteDatabase(DATABASE)


class BaseModel(Model):
    class Meta:
        database = database

class TimeSeriesDatum(BaseModel):
    """
    Model used to store `instrument` data at particular time interval.
    """
    id = BigAutoField(unique=True)
    instrument_uuid = UUIDField()
    value = FloatField()
    timestamp = BigIntegerField()
    timestep = TimeField()

class TimeSeriesImageDatum(BaseModel):
    """
    Model used to store `instrument` IMAGE bianry data at particular time interval.
    """
    id = BigAutoField(unique=True)
    instrument_uuid = UUIDField()
    value = BlobField()
    timestamp = BigIntegerField()
    timestep = TimeField()

class KeyValueItem(BaseModel):
    """
    Model used to store key-value items typically found in configurations and
    variables which we will be using to store the state of the app.
    """
    id = BigAutoField(unique=True)
    key = CharField(unique=True)
    value = CharField()
    type = IntegerField()

class PersistentStorageDataAccessObject:
    """
    Singleton class used to provide a single point of access with our local
    persistent storage with the application.
    """
    __instance = None
    __db = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if PersistentStorageDataAccessObject.__instance == None:
            PersistentStorageDataAccessObject()
        return PersistentStorageDataAccessObject.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if PersistentStorageDataAccessObject.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            PersistentStorageDataAccessObject.__instance = self
            PersistentStorageDataAccessObject.__db = database

    def beginOperation(self):
        """
        Connect with our persistent storage.
        """
        print(getDT(), "| DATABASE | Connecting to SQLite database.")
        self.__db.connect()
        self.__db.create_tables([TimeSeriesDatum, KeyValueItem, TimeSeriesImageDatum,])

    def terminateOperation(self):
        """
        Close our connection with the persistent storage.
        """
        print(getDT(), "| DATABASE | Disconnecting from SQLite database.")
        self.__db.close()

    def insertTimeSeriesDatum(self, instrument_uuid, value, timestamp, timestep):
        """
        Function will insert a new ``TimeSeriesDatum`` record into our
        persistent storage. Please note we are enforcing unique key pairs
        so we'll be only inserting unique values and not not unique pairs.
        """
        with database.atomic():
            try:
                # STEP (1): Attempt to look up and if a value was found skip insertion.
                TimeSeriesDatum.get(instrument_uuid = instrument_uuid, value=value, timestamp=timestamp, timestep=timestep)
            except Exception as e:
                print(getDT(), "| DATABASE | Saving time-series datum...")
                print(getDT(), "| DATABASE | UUID:", instrument_uuid)
                print(getDT(), "| DATABASE | Value:", value)
                print(getDT(), "| DATABASE | Timestamp:", timestamp)
                print(getDT(), "| DATABASE | Timestep:", timestep)
                # STEP (2): Insert unique key paired data.
                tsd = TimeSeriesDatum(instrument_uuid = instrument_uuid, value=value, timestamp=timestamp, timestep=timestep)
                tsd.save()
                print(getDT(), "| DATABASE | Saved.")

    def getAvailableTimeSeriesDataForSubmission(self):
        """
        Function will return all the ``TimeSeriesDatum`` objects that are older
        then the current time and are thus ready to be submitted now.
        """
        with database.atomic():
            now_ts = int(time.time())
            now_ts -= 100
            count = TimeSeriesDatum.select().where(TimeSeriesDatum.timestamp <= now_ts).count()
            return TimeSeriesDatum.select().order_by(TimeSeriesDatum.id.asc()), count

    def getAllTimeSeriesData(self):
        with database.atomic():
            timeSeriesData = TimeSeriesDatum.select().order_by(TimeSeriesDatum.id.asc())
            results = []
            for timeSeriesDatum in timeSeriesData:
                results.append({
                    'id': timeSeriesDatum.id,
                    'instrument_uuid': timeSeriesDatum.instrument_uuid,
                    'value': timeSeriesDatum.value,
                    'timestamp': timeSeriesDatum.timestamp,
                    'timestep': timeSeriesDatum.timestep,
                })
            return results

    def deleteTimeSeriesDatum(self, id):
        with database.atomic():
            print(getDT(), "| DATABASE | Deleting the following time-series datum...")
            print(getDT(), "| DATABASE | ID:", id)
            try:
                timeSeriesDatum = TimeSeriesDatum.get(TimeSeriesDatum.id == id)
                print(getDT(), "| DATABASE | UUID:", timeSeriesDatum.instrument_uuid)
                print(getDT(), "| DATABASE | Value:", timeSeriesDatum.value)
                print(getDT(), "| DATABASE | Timestamp:", timeSeriesDatum.timestamp)
                print(getDT(), "| DATABASE | Timestep:", timeSeriesDatum.timestep)
                timeSeriesDatum.delete_instance()
                print(getDT(), "| DATABASE | Deleted time-series datum.")
            except Exception as e:
                print(getDT(), "| DATABASE | Skipped deleting time-series datum.")

    def deleteSelectedTimeSeriesDatum(self, timeSeriesData):
        with database.atomic():
            print(getDT(), "| DATABASE | Deleting the following selected time-series data...")
            for timeSeriesDatum in timeSeriesData:
                print(getDT(), "| DATABASE | UUID:", timeSeriesDatum.instrument_uuid)
                print(getDT(), "| DATABASE | Value:", timeSeriesDatum.value)
                print(getDT(), "| DATABASE | Timestamp:", timeSeriesDatum.timestamp)
                print(getDT(), "| DATABASE | Timestep:", timeSeriesDatum.timestep)
                timeSeriesDatum.delete_instance()
            print(getDT(), "| DATABASE | Deleted selected time-series data.")

    def getAllTimeSeriesImageData(self):
        with database.atomic():
            timeSeriesImageData = TimeSeriesImageDatum.select().order_by(TimeSeriesImageDatum.id.asc())
            results = []
            for timeSeriesImageDatum in timeSeriesImageData:
                results.append({
                    'id': timeSeriesImageDatum.id,
                    'instrument_uuid': timeSeriesImageDatum.instrument_uuid,
                    'value': timeSeriesImageDatum.value,
                    'timestamp': timeSeriesImageDatum.timestamp,
                    'timestep': timeSeriesImageDatum.timestep,
                })
            return results

    def insertTimeSeriesImageDatum(self, instrument_uuid, image_data, timestamp, timestep):
        """
        Function will insert a new ``TimeSeriesImageDatum`` record into our
        persistent storage. Please note we are enforcing unique key pairs
        so we'll be only inserting unique values and not not unique pairs.
        """
        with database.atomic():
            try:
                # STEP (1): Attempt to look up and if a value was found skip insertion.
                TimeSeriesImageDatum.get(instrument_uuid = instrument_uuid, value=image_data, timestamp=timestamp, timestep=timestep)
            except Exception as e:
                print(getDT(), "| DATABASE | Saving time-series image datum...")
                print(getDT(), "| DATABASE | UUID:", instrument_uuid)
                print(getDT(), "| DATABASE | Value Size:", len(image_data))
                print(getDT(), "| DATABASE | Timestamp:", timestamp)
                print(getDT(), "| DATABASE | Timestep:", timestep)
                # STEP (2): Insert unique key paired data.
                tsd = TimeSeriesImageDatum(instrument_uuid = instrument_uuid, value=image_data, timestamp=timestamp, timestep=timestep)
                tsd.save()
                print(getDT(), "| DATABASE | Saved.")

    def deleteTimeSeriesImageDatum(self, id):
        with database.atomic():
            print(getDT(), "| DATABASE | Deleting the following time-series image datum...")
            print(getDT(), "| DATABASE | ID:", id)
            try:
                timeSeriesImageDatum = TimeSeriesImageDatum.get(TimeSeriesImageDatum.id == id)
                print(getDT(), "| DATABASE | UUID:", timeSeriesImageDatum.instrument_uuid)
                print(getDT(), "| DATABASE | Value Size:", len(timeSeriesImageDatum.value))
                print(getDT(), "| DATABASE | Timestamp:", timeSeriesImageDatum.timestamp)
                print(getDT(), "| DATABASE | Timestep:", timeSeriesImageDatum.timestep)
                timeSeriesImageDatum.delete_instance()
                print(getDT(), "| DATABASE | Deleted time-series image datum.")
            except Exception as e:
                print(getDT(), "| DATABASE | Skipped deleting time-series image datum.")

    def setKeyValueItem(self, key, value):
        typeOf = 0 # Do not know.
        if type(value) == int:
            typeOf = 1
        elif type(value) == str:
            typeOf = 2
        elif type(value) == float:
            typeOf = 3
        elif type(value) == bool:
            typeOf = 4
        elif type(value) == dict:
            typeOf = 5
            value = json.dumps(value)
        else:
            raise Exception("Unsupported data type detected.")
        with database.atomic():
            try:
                item = KeyValueItem.get(KeyValueItem.key == key)
                item.value = value
                item.type = typeOf
                item.save()
            except Exception as e:
                tsd = KeyValueItem(key = key, value = value, type = typeOf)
                tsd.save()

    def getValueFromKeyValueItemByKey(self, key):
        try:
            item = KeyValueItem.get(KeyValueItem.key == key)
            if item.type == 1:
                return int(item.value)
            elif item.type == 2:
                return str(item.value)
            elif item.type == 3:
                return float(item.value)
            elif item.type == 4:
                return bool(item.value)
            elif item.type == 5:
                return json.loads(item.value)
        except Exception as e:
            pass
        return None
