from gevent import monkey; monkey.patch_all()

from morning_server import stock_api
from datetime import datetime

import gevent

class StockFollower:
    def __init__(self, reader, db_col, code):
        self.reader = reader
        self.code = code
        self.started_at_startup = False
        self.db_collection = db_col

    def tick_data_handler(self, code, data):
        if len(data) != 1:
            return

        tick_data = data[0]
        self.db_collection[code].insert_one(tick_data)

    def ba_data_handler(self, code, data):
        if len(data) != 1:
            return
        ba_data = data[0]
        self.db_collection[code].insert_one(ba_data)

    def subject_handler(self, code, data):
        if len(data) != 1:
            return
        subject_data = data[0]
        self.db_collection[code].insert_one(subject_data)


    def subscribe_at_startup(self):
        self.started_at_startup = True
        stock_api.subscribe_stock(self.reader, self.code, self.tick_data_handler)
        stock_api.subscribe_stock_bidask(self.reader, self.code, self.ba_data_handler)

