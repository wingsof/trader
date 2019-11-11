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
import statistics

class PriceTrendLine:
    MINIMUM_JUMP = 3
    MINIMUM_GAP = 5.
    def __init__(self, data):
        self.i = 0
        def inc():
            self.i += 1
            return self.i
        self.price_list = list(map(lambda x: {'day': time_converter.intdate_to_datetime(x['0']), 
                                              'close': x['5'], 'xaxis': inc(), 
                                              'volume': x['6'], 'foreign': x['11']}, data))
        self.df = pd.DataFrame(self.price_list)
        self.df = self.df.set_index('day')

    def get_date(self):
        return self.price_list[-1]['day']

    def get_close_price(self):
        return self.df.close[-1]

    def get_volume(self):
        return self.df.volume[-1]

    def get_foreign(self):
        return self.df.foreign[-1]

    def is_volume_burst(self):
        recent_max = self.df.volume[-5:].max()
        if recent_max > self.df.volume[:-5].mean() * 2 and recent_max == self.df.volume.max():
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
                    slope = ((y2 - y1) / (x2 - x1))
                    if isUpperLine:
                        slope_result = False
                        if slope > 0 and (y1 - y2) / y2 * 100 > PriceTrendLine.MINIMUM_GAP:
                            #print(self.get_date(), (y1 - y2) / y2 * 100)
                            slope_result = True
                        return [v1['day'], v2['day']], [v1['close'], v2['close']], slope_result

                    else:
                        return [v1['day'], v2['day']], [v1['close'], v2['close']], slope > 0

                    
        return [], [], False

    def generate_line(self):
        upper_line = self._find_line(True)
        lower_line = self._find_line(False)

        return upper_line, lower_line


def save_as_file(df, code):
    fig = plt.figure()
    fig.patch.set_facecolor('white')
    fig.set_size_inches(18.5, 10.5)
    ax1 = fig.add_subplot(311, ylabel='price')
    ax2 = fig.add_subplot(312, ylabel='volume')
    ax3 = fig.add_subplot(313, ylabel='foreign')
    
    df['price'].plot(ax=ax1, color='r', lw=1.)
    df['volume'].plot(ax=ax2, color='g')
    df['foreign'].plot(ax=ax3, color='b')
    ax1.plot(df.ix[df.signal == True].index, 
             df.price[df.signal == True], 'v',color='k')
    ax1.plot(df.ix[df.bought == True].index, 
             df.price[df.bought == True] * 1.05, 'o',color='b')
    ax1.plot(df.ix[df.sold == True].index, 
             df.price[df.sold == True] * 1.05, 'o',color='m')
    #ax1.plot(upper_line[0], upper_line[1], color='b', lw=2., marker = 'o')
    #ax1.plot(lower_line[0], lower_line[1], color='g', lw=2., marker = 'o')

    plt.savefig(code + '.png', dpi=100)
    plt.close()


if __name__ == '__main__':
    code_list = stock_code.get_kospi200_list()
    #code_list = ['A298040']
    total_p = pd.DataFrame(columns=['code', 'profit'])
    PERIOD = 24 * 3

    for code in code_list:
        df = pd.DataFrame(columns=['code', 'date', 'price', 'trend_upper', 'trend_lower', 
                                   'signal', 'bought' , 'sold', 'volume', 'foreign', 'profit'])
        df.set_index('date')


        bought_price = 0
        total_profit = 100

        count, total = stock_chart.get_day_period_data(code, datetime(2016, 1,1), datetime(2018, 1,1))
        if count == 0:
            print("NO DATA", code)
            continue


        day_window = PERIOD + 1
        for i in range(0, count - day_window):
            data = total[i:day_window + i]
            ptl = PriceTrendLine(data)
            result = ptl.generate_line()
            bought, sold = False, False

            profit = 0
            skip_current = False
            trend_upper, trend_lower = result[0][2], result[1][2]
            if not (trend_lower and trend_upper):
                skip_current = False

            if bought_price == 0:
                if not skip_current and trend_upper and trend_lower:
                    #if ptl.is_volume_burst():
                    bought_price = ptl.get_close_price()
                    bought = True
                    #else:
                    #    skip_current = True
            else:
                current_profit = (ptl.get_close_price() - bought_price) / bought_price * 100

                if not (trend_upper and trend_lower):
                    profit = current_profit
                    total_profit = total_profit + total_profit * (ptl.get_close_price() - bought_price) / bought_price 
                    bought_price = 0
                    sold = True

            df = df.append({'code': code, 'date': ptl.get_date(), 'price': ptl.get_close_price(),
                            'trend_upper':trend_upper, 'trend_lower':trend_lower, 'signal': (trend_upper and trend_lower),
                            'bought': bought, 'sold': sold, 'volume': ptl.get_volume(), 
                            'foreign': ptl.get_foreign(), 'profit':profit
                            }, ignore_index=True)

        
        total_p = total_p.append({'code': code, 'profit': total_profit}, ignore_index=True)
        print(code, total_profit, len(df))
        
        save_as_file(df, code)
        """
        writer = pd.ExcelWriter('trendline_' + code + '.xlsx')
        df.to_excel(writer, 'Sheet1')
        writer.save()
        """
    print('AVG:', total_p['profit'].mean(), 'STD:', total_p['profit'].std())

    """

    print(code, 'profit:', total_profit)
    """
    """        
    writer = pd.ExcelWriter('total_profit.xlsx')
    total_p.to_excel(writer, 'Sheet1')
    writer.save()
    
    """