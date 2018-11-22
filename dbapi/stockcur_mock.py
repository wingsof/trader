from PyQt5.QtCore import QTimer
from pymongo import MongoClient

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dbapi import time_manager
from dbapi import config


class StockCur:
    def __init__(self, obj_id):
        self.obj_id = obj_id
        self.index = 0
        self.code = 0
        self.current_data = None
        self.event_object = None
        self.timer = QTimer()
        self.last_subscribe_time = time_manager.TimeManager.now
        self.timer.timeout.connect(self.push_data)
        self.db = MongoClient(config.MONGO_SERVER).stock

    def SetInputValue(self, index, code):
        self.index = index
        self.code = code

    def Subscribe(self):
        self.timer.start(1000)

    def Unsubscribe(self):
        self.timer.stop()

    def setEventObject(self, e):
        self.event_object = e

    def GetHeaderValue(self, index):
        return self.current_data[str(index)]

    def push_data(self):
        n = time_manager.TimeManager.now
        cursor = self.db[self.code].find({'date': 
            {'$gte': self.last_subscribe_time, '$lt': n}})
        self.last_subscribe_time = n
        for d in list(cursor):
            self.current_data = d
            self.event_object.OnReceived()


def WithEvents(obj, event_class):
    e = event_class()
    obj.setEventObject(e)
    return e
