import os
import sys

import win32com.client
from PyQt5 import QtCore
from datetime import datetime
from pymongo import MongoClient

class _CpEvent:
    def set_params(self, obj, code, db_conn):
        self.obj = obj
        self.code = code
        self.db = db_conn.stock

    def OnReceived(self):
        d = {}
        for i in range(29):
            d[str(i)] = self.obj.GetHeaderValue(i)
        d['date'] = datetime.now()

        self.db[self.code].insert_one(d)


class StockRealtime:
    def __init__(self, code, db):
        self.obj = win32com.client.Dispatch('DsCbo1.StockCur')
        self.db = db
        self.code = code

    def subscribe(self):
        handler = win32com.client.WithEvents(self.obj, _CpEvent)
        self.obj.SetInputValue(0, self.code)
        handler.set_params(self.obj, self.code, self.db)
        self.obj.Subscribe()

    def unsubscribe(self):
        self.obj.Unsubscribe()
