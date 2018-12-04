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
    from winapi import config
else:
    from dbapi import stock_chart
    from dbapi import config


_COLLECTION = 'speculation'


class Speculation:
    def __init__(self, use_cache=True):
        self.db = MongoClient(config.MONGO_SERVER).trader
        self.use_cache = use_cache

    def get_far_point(self, code, yesterday):
        collection_name = 'trend_point'
        
        cursor = self.db[collection_name].find({'code': code, 'date': yesterday})
        if self.use_cache and cursor.count() == 1:
            data = cursor.next()
            return time_converter.intdate_to_datetime(data['trend_date'])
        

        _, data = stock_chart.get_day_period_data(code, yesterday - timedelta(days=90), yesterday)
        df = pd.DataFrame(data)
        if len(df) == 0:
            return None 

        df = df.set_index('0')
        max_date = df['3'].idxmax()
        min_date = df['4'].idxmin()
        trend_date = max_date if max_date < min_date else min_date
        
        if self.use_cache:
            self.db[collection_name].insert_one({'code': code, 'date': yesterday,
                'min_date': int(min_date), 'max_date': int(max_date), 'trend_date': int(trend_date)})
        
        return time_converter.intdate_to_datetime(max_date) if max_date < min_date else time_converter.intdate_to_datetime(min_date)

    def get_speculation(self, today, code_list, method=profit_calc.MEET_DESIRED_PROFIT):
        collection_name = _COLLECTION

        if method != profit_calc.NORMAL:
            collection_name += '_' + method

        today = datetime(today.year, today.month, today.day)

        sp = pd.DataFrame(columns=['date', 'code', 'prev_close', 'buy_rate', 'sell_rate', 'profit_expected'])

        for code in code_list:
            yesterday =  today - timedelta(days=1)
            while yesterday.weekday() > 4:
                yesterday = yesterday - timedelta(days=1)

            trend_start_date = self.get_far_point(code, yesterday)

            if trend_start_date == None:
                print('warning:', code, yesterday, ' data not exist')
                continue

            cursor = self.db[collection_name].find({'code': code, 'date': yesterday, 'start_date': trend_start_date})
            if self.use_cache and cursor.count() == 1:
                c = list(cursor)
                sp = sp.append(c[0], ignore_index=True)
            else:
                _, data = stock_chart.get_day_period_data(code, trend_start_date, yesterday)
                price_list = list(map(lambda x: {'high': x['3'], 'low': x['4'], 'close': x['5']}, data))
                df = pd.DataFrame(price_list)
                buy_rate, sell_rate, profit_expected = profit_calc.get_best_rate(df, method)
                s = {'date': yesterday, 'start_date': trend_start_date,'code': code, 'prev_close': data[-1]['5'], 'buy_rate': buy_rate,
                               'sell_rate': sell_rate, 'profit_expected': profit_expected}
                sp = sp.append(s, ignore_index=True)

                if self.use_cache:
                    self.db[collection_name].insert_one(s)

        return sp

if __name__ == '__main__':
    s = Speculation()
    print(s.get_far_point('A005930', datetime(2018, 11, 25)))
