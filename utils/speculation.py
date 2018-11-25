import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from pymongo import MongoClient
from datetime import datetime, timedelta

from utils import profit_calc, time_converter

from sys import platform as _platform
if _platform == 'win32' or _platform == 'win64':
    from winapi import stock_chart
else:
    from dbapi import stock_chart

_MONGO_SERVER = 'mongodb://nnnlife.iptime.org:27017'
_COLLECTION = 'speculation'


class Speculation:
    def __init__(self, use_cache=True):
        self.db = MongoClient(_MONGO_SERVER).trader
        self.use_cache = use_cache

    def get_far_point(self, code, yesterday):
        _, data = stock_chart.get_day_period_data(code, yesterday - timedelta(days=365), yesterday)
        df = pd.DataFrame(data)
        df = df.set_index('0')
        max_date = df['3'].idxmax()
        min_date = df['4'].idxmin()

        return time_converter.intdate_to_datetime(max_date) if max_date < min_date else time_converter.intdate_to_datetime(min_date)


    def get_speculation(self, today, code_list, reverse=False):
        #print('Start Speculation')
        collection_name = _COLLECTION

        if reverse:
            collection_name += '_short'

        sp = pd.DataFrame(columns=['date', 'code', 'prev_close', 'buy_rate', 'sell_rate', 'profit_expected'])

        for code in code_list:
            yesterday =  today - timedelta(days=1)
            while yesterday.weekday() > 4:
                yesterday = yesterday - timedelta(days=1)

            trend_start_date = self.get_far_point(code, yesterday)

            cursor = self.db[collection_name].find({'code': code, 'date': yesterday, 'start_date': trend_start_date})
            if self.use_cache and cursor.count() is 1:
                c = list(cursor)
                sp = sp.append(c[0], ignore_index=True)
            else:
                _, data = stock_chart.get_day_period_data(code, trend_start_date, yesterday)
                price_list = list(map(lambda x: {'high': x['3'], 'low': x['4'], 'close': x['5']}, data))
                df = pd.DataFrame(price_list)
                buy_rate, sell_rate, profit_expected = profit_calc.get_best_rate(df, reverse)
                s = {'date': yesterday, 'start_date': trend_start_date,'code': code, 'prev_close': data[-1]['5'], 'buy_rate': buy_rate,
                               'sell_rate': sell_rate, 'profit_expected': profit_expected}
                sp = sp.append(s, ignore_index=True)

                if self.use_cache:
                    self.db[collection_name].insert_one(s)

        #print('Speculation Done', len(sp))
        return sp

if __name__ == '__main__':
    s = Speculation()
    print(s.get_far_point('A005930', datetime(2018, 11, 25)))