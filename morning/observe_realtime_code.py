import os
import sys

import win32com.client
from PyQt5 import QtCore
from datetime import datetime
from pymongo import MongoClient
from pipeline import Pipeline

# TODO: how to abstract streaming datas
from streams.stock_realtime import StockRealtime
from streams.stock_ba_realtime import StockBaRealtime

from filters.in_market_filter import InMarketFilter
from strategy.start_three_up_strategy import StartThreeUpStrategy

class ObserveRealtimeCode:
    def __init__(self, q, code):
        self.queue = q
        self.code = code
        self.stock_current = None
        self.ba_current = None
        self.bid_prices = []
        self.ask_prices = []
        self.pipeline = Pipeline()
        self.pipeline.set_elements(InMarketFilter(), StartThreeUpStrategy())

    def start_observe(self):
        if self.stock_current == None:
            self.stock_current = StockRealtime(self.code, self.process_data)
            self.stock_current.subscribe()
            self.ba_current = StockBaRealtime(self.code, self.ba_data)
            self.ba_current.subscribe()

    def process_data(self, tick):
        self.pipeline.pipe_in(tick)
        self.pipeline.result()
        #print('PUT MSG', self.msg, os.getpid())
        #self.queue.put(self.msg)
    
    def ba_data(self, tick):
        self.bid_prices = [tick['3'], tick['7'], tick['11'], tick['15'], tick['19']]
        self.ask_prices = [tick['4'], tick['8'], tick['12'], tick['16'], tick['20']]