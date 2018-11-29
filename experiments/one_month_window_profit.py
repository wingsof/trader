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
        buy_rate = sdf.iloc[0]['buy_rate']
        sell_rate = sdf.iloc[0]['sell_rate']

        _, data = stock_chart.get_day_period_data(code, today, today)
        price_list = list(map(lambda x: {'high': x['3'], 'low': x['4'], 'close': x['5']}, data))
        if len(price_list) == 0:
            print('No data')
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

        prev_close = close
        today += timedelta(days=1)

    left = money if money != 0 else bought['quantity'] * prev_close
    return left / initial_deposit * 100, trade_count

code_list = stock_code.get_kospi200_list()
start_date = datetime(2015, 11, 1)
end_date = datetime(2018, 11, 29)

method = [profit_calc.NORMAL, profit_calc.SHORT, profit_calc.MEET_DESIRED_PROFIT, profit_calc.BUY_WHEN_BEARISH]


#print(get_window_profit('A005930', start_date, end_date, profit_calc.SHORT))

for code in code_list:
    print(get_window_profit(code, start_date, end_date, profit_calc.NORMAL))
    print(get_window_profit(code, start_date, end_date, profit_calc.SHORT))
    print(get_window_profit(code, start_date, end_date, profit_calc.MEET_DESIRED_PROFIT))
    print(get_window_profit(code, start_date, end_date, profit_calc.BUY_WHEN_BEARISH))
