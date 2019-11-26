from pymongo import MongoClient
from morning.config import db
from morning.logging import logger
import pandas as pd
from morning.cybos_api import stock_chart
from utils import time_converter


class DayTick:
    def __init__(self, from_date, until_date, fetch_from_cybos, is_main_clock = False):
        self.is_main_clock = is_main_clock
        self.from_date = from_date
        self.until_date = until_date
        self.fetch_from_cybos = fetch_from_cybos
        self.save_to_excel = False
        self.next_elements = None

    def set_save_to_excel(self, is_save):
        self.save_to_excel = is_save

    def set_target(self, target):
        code = target.split(':')[1] + '_D'
        stock = MongoClient(db.HOME_MONGO_ADDRESS)['stock']
        
        if self.fetch_from_cybos:
            _, self.data = stock_chart.get_day_period_data(target.split(':')[1], self.from_date, self.until_date)
            stock[code].drop()
            stock[code].insert_many(self.data)
        else:
            s = time_converter.datetime_to_intdate(self.from_date)
            f = time_converter.datetime_to_intdate(self.until_date)
            cursor = stock[code].find({'0': {'$gte':s, '$lte': f}})
            self.data = list(cursor)

        logger.print(target, 'Length', len(self.data))

    def set_output(self, next_ele):
        self.next_elements = next_ele

    def received(self, data):
        if len(self.data) > 0:
            d = self.data.pop(0)

            if self.next_elements:
                self.next_elements.received([d])
        return len(self.data)

    def is_realtime(self):
        return False

    def have_clock(self):
        return True
    
        


