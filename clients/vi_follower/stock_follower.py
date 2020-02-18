from gevent import monkey; monkey.patch_all()

from morning_server import stock_api
from datetime import datetime

import gevent

class StockFollower:
    def __init__(self, reader, db_col, code, yesterday_data):
        self.reader = reader
        self.code = code
        self.started_at_startup = False
        self.db_collection = db_col
        # yesterday data is None when newly stocked today
        # additionally sometimes market code does not contain VI code why?
        self.yesterday_data = yesterday_data

    def tick_data_handler(self, code, data):
        if len(data) != 1:
            return

        tick_data = data[0]
        self.db_collection[code].insert_one(tick_data)
        #print('TICK', code)

    def ba_data_handler(self, code, data):
        if len(data) != 1:
            return
        ba_data = data[0]
        self.db_collection[code].insert_one(ba_data)
        #print('BA', code)

    def subject_handler(self, code, data):
        if len(data) != 1:
            return
        subject_data = data[0]
        self.db_collection[code].insert_one(subject_data)
        #print('SUBJECT', subject_data)


    def start_watch(self):
        # Test min_data since have a conflict
        # Disable minute data since purpose is collect data
        #min_data = stock_api.request_stock_today_data(self.reader, self.code)
        print('Subscribe Start', self.code)
        stock_api.subscribe_stock(self.reader, self.code, self.tick_data_handler)
        stock_api.subscribe_stock_bidask(self.reader, self.code, self.ba_data_handler)
        stock_api.subscribe_stock_subject(self.reader, self.code, self.subject_handler)
        return True
        #return False

    def subscribe_at_startup(self):
        self.started_at_startup = True
        stock_api.subscribe_stock(self.reader, self.code, self.tick_data_handler)
        stock_api.subscribe_stock_bidask(self.reader, self.code, self.ba_data_handler)
        stock_api.subscribe_stock_subject(self.reader, self.code, self.subject_handler)

