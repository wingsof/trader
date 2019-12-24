import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import win32com.client
from PyQt5 import QtCore
from datetime import datetime
from winapi import config
from pymongo import MongoClient

class _CpEvent:
    def set_params(self, obj, code, db):
        self.obj = obj
        self.code = code
        self.db = db

    def OnReceived(self):
        d = {}
        for i in range(29):
            d[str(i)] = self.obj.GetHeaderValue(i)
        d['date'] = datetime.now()

        self.db[self.code].insert_one(d)


class _StockRealtime:
    def __init__(self, code, current_obj, db):
        self.obj = win32com.client.Dispatch('DsCbo1.StockCur')
        self.code = code
        self.current_obj = current_obj
        self.db = db

    def subscribe(self):
        handler = win32com.client.WithEvents(self.obj, _CpEvent)
        self.obj.SetInputValue(0, self.code)
        handler.set_params(self.obj, self.code, self.db)
        self.obj.Subscribe()

    def unsubscribe(self):
        self.obj.Unsubscribe()


class StockCurrent:
    def __init__(self, code_list):
        self.code_list = code_list
        self.realtime_bucket = []
        self.buy_dict = {}
        self.sell_dict = {}
        self.client = MongoClient(config.MONGO_SERVER)

        for code in self.code_list:
            self.realtime_bucket.append(_StockRealtime(code, self, self.client.stock))

    def stop(self):
        for r in self.realtime_bucket:
            r.unsubscribe()

    def start(self):
        for r in self.realtime_bucket:
            r.subscribe()

    def add_to_buy_cart(self, code, expected):
        if expected > 110.:
            print('BUY CART(%d)' % len(self.buy_dict), code, expected, flush=True)
            self.buy_dict[code] = [expected, 0]

    def add_to_sell_cart(self, code):
        print('SELL CART(%d)' % len(self.sell_dict), code, flush=True)
        self.sell_dict[code] = [0, 0]

    def cancel_to_buy_cart(self, code):
        self.buy_dict.pop(code, None)

    def set_sell_price(self, code, price):
        if code in self.sell_dict:
            self.sell_dict[code][1] = price
    
    def set_buy_price(self, code, price):
        if code in self.buy_dict:
            self.buy_dict[code][1] = price

    def get_buy_dict(self):
        return self.buy_dict

    def get_sell_dict(self):
        return self.sell_dict
