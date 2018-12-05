import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import speculation, profit_calc
from dbapi import stock_code, stock_chart
import pandas as pd
from datetime import datetime, timedelta
import numpy as np


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

        s = speculation.Speculation()
        sdf = s.get_speculation(today, [code], profit_calc.NORMAL)
        if len(sdf) == 0:
            today += timedelta(days=1)
            continue

        ssdf = s.get_speculation(today, [code], profit_calc.SHORT)

        buy_rate = sdf.iloc[0]['buy_rate']
        sell_rate = sdf.iloc[0]['sell_rate']
        sbuy_rate = ssdf.iloc[0]['buy_rate']
        ssell_rate = ssdf.iloc[0]['sell_rate']

        _, data = stock_chart.get_day_period_data(code, today, today)
        price_list = list(map(lambda x: {'high': x['3'], 'low': x['4'], 'close': x['5']}, data))
        if len(price_list) == 0:
            print('No data')
            today += timedelta(days=1)
            continue
        elif len(price_list) > 1:
            print('Something wrong', today)

        low = price_list[0]['low']
        high = price_list[0]['high']
        close = price_list[0]['close']
        buy_threshold = prev_close * buy_rate
        sell_threshold = prev_close * sell_rate
        
        ex_condition = sdf.iloc[0]['profit_expected'] > ssdf.iloc[0]['profit_expected'] and ssdf.iloc[0]['profit_expected'] < 100.0 and sdf.iloc[0]['profit_expected'] >= 110.

        if bought['quantity'] != 0 and not ex_condition:
            money = close * bought['quantity']
            money -= money * 0.003
            bought['quantity'] = 0
        elif bought['quantity'] == 0 and ex_condition and prev_close != 0:
            bought['quantity'] = money / close
            money = 0
            trade_count += 1

        if initial_price == 0:
            initial_price = close

        prev_close = close
        left = money if money != 0 else bought['quantity'] * prev_close
        
        yield today, left / initial_deposit * 100, sdf.iloc[0]['profit_expected'], ssdf.iloc[0]['profit_expected'], buy_rate, sell_rate, close / initial_price * 100, trade_count
        print(today, 'P:', '{0:0.3f}'.format(left / initial_deposit * 100), 'E:', '{0:0.3f}'.format(sdf.iloc[0]['profit_expected']), 'SE:', '{0:0.3f}'.format(ssdf.iloc[0]['profit_expected']), '{0:0.3f}'.format(buy_rate), '{0:0.3f}'.format(sell_rate), '{0:0.3f}'.format(close / initial_price * 100))
        today += timedelta(days=1)

#code_list = ['A005930']
code_list = [sys.argv[1]]
start_date = datetime(2015, 11, 1)
end_date = datetime(2018, 11, 29)

df = pd.DataFrame(columns=['date', 'profit', 'expected', 'short_expected', 'buy_threshold', 'sell_threshold', 'price'])

for code in code_list:
    for date, profit, expected, se, buy_t, sell_t, p, tcount in get_window_profit(code, start_date, end_date):
        df = df.append({'date': date, 'profit': profit, 'expected': expected, 'short_expected': se,'buy_threshold': buy_t,
                    'sell_threshold': sell_t, 'price': p}, ignore_index=True)

writer = pd.ExcelWriter(sys.argv[1] + '_new.xlsx')
df.to_excel(writer, 'Sheet1')
writer.save()
