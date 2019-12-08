from pymongo import MongoClient
from morning.config import db
from utils import time_converter
from morning.logging import logger
from datetime import datetime
from morning.back_data import fetch_stock_data

class MinTick:
    def __init__(self, date, is_main_clock=True):
        self.is_main_clock = is_main_clock
        self.date = date
        self.target_code = ''
        self.next_elements = None

    def finalize(self):
        if self.next_elements:
            self.next_elements.finalize()

    def set_target(self, target):
        code = target.split(':')[1]
        self.target_code = code
        self.data = fetch_stock_data.get_day_minute_period_data_force_from_db(code, self.date, self.date)
        #logger.print(target, 'Length', len(self.data))
        print('Length', len(self.data))

    def set_output(self, next_ele):
        self.next_elements = next_ele

    def received(self, _):
        if len(self.data) > 0:
            d = self.data.pop(0)
            d['date'] =  datetime(int(d['0'] / 10000), int(d['0'] % 10000 / 100), int(d['0'] % 100), int(d['1'] / 100), int(d['1'] % 100))
            d['stream'] = self.__class__.__name__
            d['target'] = self.target_code
            if self.next_elements:
                self.next_elements.received([d])

        return len(self.data)

    def is_realtime(self):
        return False

    def have_clock(self):
        return self.is_main_clock
