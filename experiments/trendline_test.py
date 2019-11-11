import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import time_converter
from dbapi import stock_code, stock_chart
import pandas as pd
from datetime import datetime
from datetime import date
from datetime import timedelta
import matplotlib.pyplot as plt
import numpy as np


class PriceTrendLine:
    MINIMUM_JUMP = 5

    def __init__(self, data):
        self.i = 0
        def inc():
            self.i += 1
            return self.i
        self.price_list = list(map(lambda x: {'day': time_converter.intdate_to_datetime(x['0']), 'close': x['5'], 'xaxis': inc(), 'volume': x['6']}, data))
        self.df = pd.DataFrame(self.price_list)
        self.df = self.df.set_index('day')

    def get_date(self):
        return self.price_list[-1]['day']

    def get_close_price(self):
        return self.df.close[-1]

    def is_volume_burst(self):
        one_month_max = self.df.volume[-30:].max()
        if self.df.volume[-5:].max() > self.df.volume[:-5].mean() * 2 and self.df.volume[-5:].max() == one_month_max:
            return True

    def _find_line(self, isUpperLine):
        for i, v1 in enumerate(reversed(self.price_list)):
            left_jump_index = len(self.price_list) - i  - PriceTrendLine.MINIMUM_JUMP
            if left_jump_index < 0:
                left_jump_index = 0

            for v2 in reversed(self.price_list[:left_jump_index]):
                if v1['day'] == v2['day']: continue
                # (y1 - y2) * x + (x2 - x1) * y + x1 * y2 - x2 * y1 = 0
                found = True
                for c in self.price_list:
                    if c['day'] == v1['day'] or c['day'] == v2['day']: continue
                    x1, x2, y1, y2, cx, cy = v1['xaxis'], v2['xaxis'], v1['close'], v2['close'], c['xaxis'], c['close']
                    result = (y1 - y2) * cx + (x2 - x1) * cy + x1 * y2 - x2 * y1
                    
                    if (isUpperLine and result < 0) or (not isUpperLine and result > 0) :
                        found = False
                        #print('Faled')
                        break

                if found:
                    x1, x2, y1, y2 = v1['xaxis'], v2['xaxis'], v1['close'], v2['close']
                    return [v1['day'], v2['day']], [v1['close'], v2['close']], ((y2 - y1) / (x2 - x1)) > 0

    def generate_line(self):
        upper_line = self._find_line(True)
        lower_line = self._find_line(False)

        return upper_line, lower_line


if __name__ == '__main__':
    #code_list = stock_code.get_kospi200_list()
    code_list = ['A003850', 'A047050', 'A001740']

    for loss in [-2]:
        total_p = pd.DataFrame(columns=['code', 'profit'])
        for code in code_list:
            df = pd.DataFrame(columns=['code', 'date', 'price', 'trend_upper', 'trend_lower', 'buy_price', 'sell_price', 'profit'])

            today =  datetime(2015, 1,1)
            bought_price = 0
            total_profit = 100
            skip_flow = False
            
            count, total = stock_chart.get_day_period_data(code, today, datetime.now())

            day_window = 91 - 24 # 3 month + 1 day
            for i in range(0, count - day_window):
                data = total[i:day_window + i]
                ptl = PriceTrendLine(data)
                result = ptl.generate_line()

                sell_price = 0
                profit = 0
                trend_upper, trend_lower = result[0][2], result[1][2]

                if not (trend_upper and trend_lower):
                    skip_flow = False

                if bought_price > 0 and not (trend_upper and trend_lower):
                    sell_price = ptl.get_close_price()
                    profit = (sell_price - bought_price) / bought_price * 100
                    total_profit = total_profit + total_profit * (sell_price - bought_price) / bought_price 
                    bought_price = 0
                elif bought_price > 0 and (ptl.get_close_price() - bought_price) / bought_price * 100 < loss:
                    skip_flow = True
                    sell_price = ptl.get_close_price()
                    profit = (sell_price - bought_price) / bought_price * 100
                    total_profit = total_profit + total_profit * (sell_price - bought_price) / bought_price 
                    bought_price = 0                    
                elif bought_price == 0 and not skip_flow and trend_upper and trend_lower:
                    if ptl.is_volume_burst():
                        bought_price = ptl.get_close_price()
                    else:
                        skip_flow = True

                df = df.append({'code': code, 'date': ptl.get_date(), 'price': ptl.get_close_price(),
                                'trend_upper':trend_upper, 'trend_lower':trend_lower, 
                                'buy_price':bought_price, 'sell_price': sell_price, 
                                'profit':profit
                                }, ignore_index=True)
            
            writer = pd.ExcelWriter('trendline_' + code + '.xlsx')
            df.to_excel(writer, 'Sheet1')
            writer.save()