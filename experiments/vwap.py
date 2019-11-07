import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import time_converter
from dbapi import stock_chart
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np


class Vwap:
    def __init__(self, data):
        self.df = pd.DataFrame(list(map(lambda x: {'date': time_converter.intdate_to_datetime(x['0']), 
                                                   'close': x['5'], 
                                                   'high' : x['3'],
                                                   'low' : x['4'],
                                                   'end' : x['5'],
                                                   'volume' : x['6']}, data)))
        self.df = self.df.set_index('date')

    def generate_signals(self):
        self.df['price_mul_vol'] = (self.df['high'] + self.df['low'] + self.df['end']) / 3 * self.df['volume']
        self.df['vwap'] = self.df['price_mul_vol'] / self.df['volume'].sum()
        print('sum', self.df['volume'].sum())
        print(self.df)


if __name__ == '__main__':
    _, data = stock_chart.get_day_period_data('A005380', datetime(2015, 1, 1), datetime(2018, 11, 30))
    # 2 start, 3 high, 4 low, 5 end
    mac = Vwap(data)
    mac.generate_signals()
    
    fig = plt.figure()
    fig.patch.set_facecolor('white')
    ax1 = fig.add_subplot(311, ylabel='price')
    ax2 = fig.add_subplot(312, ylabel='vwap')
    ax3 = ax2.twinx()


    mac.df['close'].plot(ax=ax1, color='r', lw=2.)
    mac.df['vwap'].plot(ax=ax2, color='b')
    mac.df['volume'].plot(ax=ax3, color='g')

    plt.show()
