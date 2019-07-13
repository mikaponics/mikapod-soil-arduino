#!/usr/bin/python
# -*- coding: utf-8 -*-
import Pyro4
import serpent

from foundation import *
from persistent_storage import PersistentStorageDataAccessObject

"""
Application used to provide remote methods calls to the local storage data.
"""

@Pyro4.expose
class PersistentStorage(object):
    """
    Remote procedure call interface
    """

    def __init__(self):
        self.__storage = PersistentStorageDataAccessObject.getInstance()

    def getAllTimeSeriesData(self):
        return self.__storage.getAllTimeSeriesData()

    def insertTimeSeriesDatum(self, instrument_uuid, value, timestamp, timestep):
        return self.__storage.insertTimeSeriesDatum(instrument_uuid, value, timestamp, timestep)

    def deleteTimeSeriesDatum(self, id):
        return self.__storage.deleteTimeSeriesDatum(id)

    def setKeyValueItem(self, key, value):
        return self.__storage.setKeyValueItem(key, value)

    def getValueFromKeyValueItemByKey(self, key):
        return self.__storage.getValueFromKeyValueItemByKey(key)

    def getAllTimeSeriesImageData(self):
        return self.__storage.getAllTimeSeriesImageData()

    def insertTimeSeriesImageDatum(self, instrument_uuid, image_info, timestamp, timestep):
        # DEVELOPERS NOTE:
        # - READ: https://pythonhosted.org/Pyro4/tipstricks.html?highlight=image#binarytransfer
        # - In essence we need to use the `serpent` library to deserialize and convert to binary.
        image_data = serpent.tobytes(image_info)   # in case of serpent encoded bytes
        return self.__storage.insertTimeSeriesImageDatum(instrument_uuid, image_data, timestamp, timestep)

    def deleteTimeSeriesImageDatum(self, id):
        return self.__storage.deleteTimeSeriesImageDatum(id)


class MikapodPersistentStorageService(object):

    def __init__(self):
        self.__storage = PersistentStorageDataAccessObject.getInstance()
        self.__storage.beginOperation()

    def runOnMainLoop(self):
        daemon = Pyro4.Daemon()                    # make a Pyro daemon
        ns = Pyro4.locateNS()                      # find the name server
        uri = daemon.register(PersistentStorage)   # register the greeting maker as a Pyro object
        ns.register("mikapod.storage", uri)        # register the object with a name in the name server

        print(getDT(), "| STORAGE | Ready")
        daemon.requestLoop()                   # start the event loop of the server to wait for calls


if __name__ == "__main__":
    """
    Main entry into the main program.
    """
    app = MikapodPersistentStorageService()
    app.runOnMainLoop()
