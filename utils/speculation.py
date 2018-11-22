import pandas as pd
from pymongo import MongoClient
from datetime import datetime, timedelta

from utils import profit_calc

from sys import platform as _platform
if _platform == 'win32' or _platform == 'win64':
    from winapi import stock_chart
else:
    from dbapi import stock_chart

_MONGO_SERVER = 'mongodb://nnnlife.iptime.org:27017'
_COLLECTION = 'speculation'


class Speculation:
    def __init__(self):
        self.db = MongoClient(_MONGO_SERVER).speculation


    def get_speculation(self, today, code_list):
        print('Start Speculation')
        sp = pd.DataFrame(columns=['date', 'code', 'prev_close', 'buy_rate', 'sell_rate', 'profit_expected'])

        for code in code_list:
            d = datetime(today.year, today.month, today.day)

            cursor = self.db[_COLLECTION].find({'code': code, 'date': d})
            if cursor.count() is 1:
                c = list(cursor)
                sp = sp.append(c[0], ignore_index=True)
            else:
                yesterday =  today - timedelta(days=1)
                l, data = stock_chart.get_day_period_data(code, yesterday - timedelta(days=30), yesterday)
                price_list = list(map(lambda x: {'high': x['3'], 'low': x['4'], 'close': x['5']}, data))
                df = pd.DataFrame(price_list)
                buy_rate, sell_rate, profit_expected = profit_calc.get_best_rate(df)
                s = {'date': d, 'code': code, 'prev_close': data[-1]['5'], 'buy_rate': buy_rate,
                               'sell_rate': sell_rate, 'profit_expected': profit_expected}
                sp = sp.append(s, ignore_index=True)
                self.db[_COLLECTION].insert_one(s)

        print('Speculation Done', len(sp))
        return sp

