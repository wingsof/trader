import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import time_converter
from dbapi import stock_chart
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np


class MovingAverageCross:
    def __init__(self, data, short_ma, long_ma):
        self.short_ma = short_ma
        self.long_ma = long_ma
        self.df = pd.DataFrame(list(map(lambda x: {'date': time_converter.intdate_to_datetime(x['0']), 'close': x['5']}, data)))
        self.df = self.df.set_index('date')

    def generate_signals(self):
        self.df['signal'] = 0.0
        self.df['short_mavg'] = self.df['close'].rolling(self.short_ma, min_periods=1).mean()
        self.df['long_mavg'] = self.df['close'].rolling(self.long_ma, min_periods=1).mean()
        self.df['signal'][self.short_ma:] = np.where(self.df['short_mavg'][self.short_ma:] > self.df['long_mavg'][self.short_ma:], 1.0, 0.0)
        self.df['positions'] = self.df['signal'].diff()
        print(self.df)


if __name__ == '__main__':
    _, data = stock_chart.get_day_period_data('A005380', datetime(2015, 1, 1), datetime(2018, 11, 30))
    mac = MovingAverageCross(data, 20, 120)
    mac.generate_signals()
    fig = plt.figure()
    fig.patch.set_facecolor('white')
    ax1 = fig.add_subplot(111, ylabel='price')
    mac.df['close'].plot(ax=ax1, color='r', lw=2.)
    mac.df[['short_mavg', 'long_mavg']].plot(ax=ax1, lw=2.)

    ax1.plot(mac.df.ix[mac.df.positions == -1.0].index, 
            mac.df.close[mac.df.positions == -1.0], 'v',
            markersize=10, color='k')

    ax1.plot(mac.df.ix[mac.df.positions == 1.0].index,
            mac.df.close[mac.df.positions == 1.0],
            '^', markersize=10, color='m')
    plt.show()
