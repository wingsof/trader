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
def get_window_profit(code, start_date, end_date, method):
    initial_deposit = 10000000
    initial_price = 0
    money = initial_deposit
    prev_close = 0
    bought = {'quantity': 0, 'price': 0, 'balance': 0}
    trade_count = 0
    method_apply = {
        profit_calc.NORMAL: profit_calc.right_profit,
        profit_calc.SHORT: profit_calc.short_profit,
        profit_calc.MEET_DESIRED_PROFIT: profit_calc.right_sell_profit,
        profit_calc.BUY_WHEN_BEARISH: profit_calc.left_profit
    }

    today = start_date
    while today < end_date:
        while today.weekday() > 4:
            today += timedelta(days=1)

        s = speculation.Speculation()
        sdf = s.get_speculation(today, [code], method)
        if len(sdf) == 0:
            today += timedelta(days=1)
            continue

        buy_rate = sdf.iloc[0]['buy_rate']
        sell_rate = sdf.iloc[0]['sell_rate']

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
        
        money, t = method_apply[method](bought, low, high, close,
                prev_close, buy_threshold, sell_threshold, money, trade_count)
        trade_count += t

        if initial_price == 0:
            initial_price = close

        prev_close = close
        if method == profit_calc.SHORT:
            left = money if money is not 0 else (bought['price'] - prev_close) * bought['quantity'] + bought['balance']
        else:
            left = money if money != 0 else bought['quantity'] * prev_close
        
        yield today, left / initial_deposit * 100, sdf.iloc[0]['profit_expected'], buy_rate, sell_rate, close / initial_price * 100, trade_count
        today += timedelta(days=1)


code_list = ['A005930']
start_date = datetime(2015, 11, 1)
end_date = datetime(2018, 11, 29)

method = [profit_calc.NORMAL, profit_calc.SHORT, profit_calc.MEET_DESIRED_PROFIT, profit_calc.BUY_WHEN_BEARISH]

df = pd.DataFrame(columns=['date', 'profit', 'expected', 'buy_threshold', 'sell_threshold', 'price', 'method'])

for code in code_list:
    for m in method:
        for date, profit, expected, buy_t, sell_t, p, tcount in get_window_profit(code, start_date, end_date, m):
            df = df.append({'date': date, 'profit': profit, 'expected': expected, 'buy_threshold': buy_t,
                        'sell_threshold': sell_t, 'price': p, 'method': m}, ignore_index=True)

writer = pd.ExcelWriter('a005930.xlsx')
df.to_excel(writer, 'Sheet1')
writer.save()
