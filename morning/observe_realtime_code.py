import os
import sys

import win32com.client
from PyQt5 import QtCore
from datetime import datetime
from pymongo import MongoClient
from pipeline import Pipeline


class _CpEvent:
    def set_params(self, obj, code, callback):
        self.obj = obj
        self.code = code
        self.callback = callback

    def OnReceived(self):
        d = {}
        for i in range(29):
            d[str(i)] = self.obj.GetHeaderValue(i)
        d['date'] = datetime.now()
        self.callback(d)


class StockRealtime:
    def __init__(self, code, callback):
        self.obj = win32com.client.Dispatch('DsCbo1.StockCur')
        self.code = code
        self.callback = callback
        # construct pipeline

    def subscribe(self):
        handler = win32com.client.WithEvents(self.obj, _CpEvent)
        self.obj.SetInputValue(0, self.code)
        handler.set_params(self.obj, self.code, self.callback)
        self.obj.Subscribe()

    def unsubscribe(self):
        self.obj.Unsubscribe()


from filters.in_market_filter import InMarketFilter
from strategy.start_three_up_strategy import StartThreeUpStrategy

class ObserveRealtimeCode:
    def __init__(self, q, code):
        self.queue = q
        self.code = code
        self.pipeline = Pipeline()
        self.pipeline.set_elements(InMarketFilter(), StartThreeUpStrategy())

    def start_observe(self):
        self.stock_current = StockRealtime(self.code, self.process_data)

    def process_data(self, tick):
        process = self.pipeline.stream_in_data(tick)
        result = process.result()
        #print('PUT MSG', self.msg, os.getpid())
        #self.queue.put(self.msg)