from datetime import datetime
import pandas as pd
from pymongo import MongoClient
from morning.config import db
from utils import time_converter

class DayProfitCompareAccount:
    def __init__(self, option_name, use_cybos=False):
        self.option = 0
        self.option_name = option_name
        self.use_cybos = use_cybos

        self.df = pd.DataFrame(columns = ['date', option_name, 'code', 'max_profit'])
        self.option_set = set()

    def set_up(self, c):
        self.option = c
        self.option_set.add(c)

    def get_highest_price(self, date, code, price):
        if self.use_cybos:
            from morning.cybos_api import stock_chart
            l, data = stock_chart.get_day_period_data(code, date, date)
            if l == 1:
                return data[0]['3']
        else:
            stock_db = MongoClient(db.HOME_MONGO_ADDRESS)['stock']
            d = time_converter.datetime_to_intdate(date)
            cursor = stock_db[code + '_D'].find({'0': {'$gte':d, '$lte': d}})
        
            if cursor.count() == 1:
                return (list(cursor))[0]['3']

        return price


    def summary(self):
        for c in self.option_set:
            max_profit = self.df[self.df[self.option_name] == c]['max_profit']
            print(c, 'PROFIT avg:', max_profit.mean(), 'std:', max_profit.std())
        self.df.to_excel(self.option_name + '.xlsx')


    def transaction(self, msg):
        buy, code, price, date = msg['result'], msg['target'], msg['value'], msg['date']
        stream_name, strategy = msg['stream'], msg['strategy']

        price = float(price)
        if buy:
            if strategy == 'YdayCloseTodayStart':
                row = {'date': date, self.option_name: self.option,
                        'code': code, 'max_profit': price}
                self.df = self.df.append(row, ignore_index = True)
            else:
                highest_price = self.get_highest_price(date, code, price)
                row = {'date': date, self.option_name: self.option,
                        'code': code, 'max_profit': (highest_price - price) / price * 100}
                self.df = self.df.append(row, ignore_index = True)

                