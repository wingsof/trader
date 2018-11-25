# get speculation from 2018. 10. 22 and get real profit
# compare expectation and real profit

from utils import speculation, profit_calc
from dbapi import stock_code, stock_chart
import pandas as pd
from datetime import datetime, timedelta
import numpy as np



def get_window_profit(code, start_date, end_date, use_close_price):
    initial_deposit = 10000000
    money = initial_deposit
    prev_close = 0
    bought = {'quantity': 0, 'price': 0}
    trade_count = 0

    while end_date > start_date:
        start_date += timedelta(days=1)

        s = speculation.Speculation()

        sp_list = s.get_speculation(start_date, [code])
        df = pd.DataFrame(sp_list)

        l, data = stock_chart.get_day_period_data(code, start_date, start_date + timedelta(days=1))
        if l == 0: continue

        high, low, close = data[0]['3'], data[0]['4'], data[0]['5']    
        buy_rate = df[df['code'] == code].iloc[0]['buy_rate']
        sell_rate = df[df['code'] == code].iloc[0]['sell_rate']
        print(df[df['code'] == code].iloc[0]['date'], buy_rate, sell_rate, df[df['code'] == code].iloc[0]['profit_expected'])
        buy_threshold = prev_close * buy_rate
        sell_threshold = prev_close * sell_rate

        if bought['quantity'] is not 0 and low <= prev_close - sell_threshold:
            if use_close_price:
                money = close * bought['quantity']
            else:
                money = (prev_close - sell_threshold) * bought['quantity']
            money -= money * 0.003
            bought['quantity'] = 0
        elif bought['quantity'] is 0 and prev_close != 0 and high >= prev_close + buy_threshold:
            if use_close_price:
                bought['quantity'] = money / close
            else:
                bought['quantity'] = money / (prev_close + buy_threshold)

            money = 0
            trade_count += 1


        prev_close = close

    left = money if money is not 0 else bought['quantity'] * prev_close
    return (left / initial_deposit * 100, trade_count)


code_list = stock_code.get_kospi200_list()
start_date = datetime(2018, 11, 25)
end_date = datetime(2018, 11, 26)

for code in code_list:
    print(get_window_profit(code, start_date, end_date, True))