import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import time_converter
from dbapi import stock_chart
import pandas as pd
from datetime import datetime
from datetime import date
from datetime import timedelta
import matplotlib.pyplot as plt
import numpy as np


class PriceTrendLine:
    MINIMUM_JUMP = 2

    def __init__(self, data):
        self.i = 0
        def inc():
            self.i += 1
            return self.i
        self.price_list = list(map(lambda x: {'date': time_converter.intdate_to_datetime(x['0']), 'close': x['5'], 'xaxis': inc()}, data))
        self.df = pd.DataFrame(self.price_list)
        self.df = self.df.set_index('date')

    def _find_line(self, isUpperLine):
        for i, v1 in enumerate(reversed(self.price_list)):
            left_jump_index = len(self.price_list) - i  - int(len(self.price_list) / 10)
            if left_jump_index < 0:
                left_jump_index = 0

            for v2 in reversed(self.price_list[:left_jump_index]):
                if v1['date'] == v2['date']: continue
                # (y1 - y2) * x + (x2 - x1) * y + x1 * y2 - x2 * y1 = 0
                found = True
                for c in self.price_list:
                    if c['date'] == v1['date'] or c['date'] == v2['date']: continue
                    x1, x2, y1, y2, cx, cy = v1['xaxis'], v2['xaxis'], v1['close'], v2['close'], c['xaxis'], c['close']
                    result = (y1 - y2) * cx + (x2 - x1) * cy + x1 * y2 - x2 * y1
                    
                    if (isUpperLine and result < 0) or (not isUpperLine and result > 0) :
                        found = False
                        #print('Faled')
                        break
                    #if not isUpperLine:
                    #    print(result, v1['date'], v2['date'], c['date'])
                if found:
                    if not isUpperLine: print('Success')
                    return [v1['date'], v2['date']], [v1['close'], v2['close']]

    def generate_line(self):
        upper_line = self._find_line(True)
        lower_line = self._find_line(False)

        return upper_line, lower_line

if __name__ == '__main__':
    _, data = stock_chart.get_day_period_data('A005930', date.today() - timedelta(days=90), datetime(2019,10,22))
    mac = PriceTrendLine(data)
    upper_line, lower_line = mac.generate_line()
    fig = plt.figure()
    fig.patch.set_facecolor('white')
    ax1 = fig.add_subplot(111, ylabel='price')
    mac.df['close'].plot(ax=ax1, color='r', lw=2.)
    ax1.plot(upper_line[0], upper_line[1], color='b', lw=2., marker = 'o')
    ax1.plot(lower_line[0], lower_line[1], color='g', lw=2., marker = 'o')

    plt.show()
