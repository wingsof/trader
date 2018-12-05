import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import speculation, profit_calc, time_converter
from dbapi import stock_code, stock_chart
import pandas as pd
from datetime import datetime, timedelta
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




# use speculation to get past parameter to buy and sell
# get result profit for 1 year
def get_window_profit(code, start_date, end_date):
    initial_deposit = 10000000
    initial_price = 0
    money = initial_deposit
    prev_close = 0
    bought = {'quantity': 0, 'price': 0, 'balance': 0}
    trade_count = 0
    
    today = start_date
    while today < end_date:
        while today.weekday() > 4:
            today += timedelta(days=1)

        _, today_data = stock_chart.get_day_period_data(code, today, today)
        price_list = list(map(lambda x: {'high': x['3'], 'low': x['4'], 'close': x['5']}, today_data))

        if len(price_list) == 0:
            print('No data')
            today += timedelta(days=1)
            continue

        _, data = stock_chart.get_day_period_data(code, today - timedelta(days=200), today - timedelta(days=1))

        low = price_list[0]['low']
        high = price_list[0]['high']
        close = price_list[0]['close']

        mac = MovingAverageCross(data, 20, 120)
        mac.generate_signals()
        last_position = mac.df.signal[-1]


        if bought['quantity'] != 0 and last_position == 0:
            money = close * bought['quantity']
            money -= money * 0.003
            print('SELL', close)
            bought['quantity'] = 0
        elif bought['quantity'] == 0 and last_position == 1 and prev_close != 0:
            bought['quantity'] = money / close
            money = 0
            trade_count += 1
            print('BUY', close)

        if initial_price == 0:
            initial_price = close

        prev_close = close
        left = money if money != 0 else bought['quantity'] * prev_close
        
        yield today, left / initial_deposit * 100, last_position, close / initial_price * 100, trade_count
        print(today, 'P:', '{0:0.3f}'.format(left / initial_deposit * 100), 'POS:', last_position, '{0:0.3f}'.format(close / initial_price * 100))
        today += timedelta(days=1)

#code_list = ['A005930']
code_list = [sys.argv[1]]
start_date = datetime(2015, 1, 1)
end_date = datetime(2018, 11, 29)

df = pd.DataFrame(columns=['date', 'profit', 'pos', 'price'])

for code in code_list:
    for date, profit, pos, p, tcount in get_window_profit(code, start_date, end_date):
        df = df.append({'date': date, 'profit': profit, 'pos': pos, 'price': p}, ignore_index=True)

writer = pd.ExcelWriter(sys.argv[1] + '_sma.xlsx')
df.to_excel(writer, 'Sheet1')
writer.save()
