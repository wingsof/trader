# get speculation from 2018. 10. 22 and get real profit
# compare expectation and real profit

from utils import speculation, profit_calc
from dbapi import stock_code, stock_chart
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

np.set_printoptions(precision=3)

def get_window_profit(code, start_date, end_date, buy_rate, sell_rate):
    initial_deposit = 10000000
    money = initial_deposit
    prev_close = 0
    bought = {'quantity': 0, 'price': 0}
    trade_count = 0

    while end_date > start_date:
        start_date += timedelta(days=1)

        l, data = stock_chart.get_day_period_data(code, start_date, start_date + timedelta(days=1))
        if l == 0: continue

        high, low, close = data[0]['3'], data[0]['4'], data[0]['5']    

        buy_threshold = prev_close * buy_rate
        sell_threshold = prev_close * sell_rate

        if bought['quantity'] is not 0 and low <= prev_close - sell_threshold:
            money = close * bought['quantity']
            money -= money * 0.003
            bought['quantity'] = 0
        elif bought['quantity'] is 0 and prev_close != 0 and high >= prev_close + buy_threshold:
            bought['quantity'] = money / close
            money = 0
            trade_count += 1


        prev_close = close

    left = money if money is not 0 else bought['quantity'] * prev_close
    return (left / initial_deposit * 100, trade_count)



code = 'A005380'

start_date = datetime(2016, 1, 1)
end_date = datetime(2017, 1, 1)

buy_t_list = list(np.arange(0.01, 0.065, 0.005))
sell_t_list = list(np.arange(0.01, 0.065, 0.005))
#buy_t_list = [0.036]
#sell_t_list = [0.013]
for buy_rate in buy_t_list:
    for sell_rate in sell_t_list:
        print('{0:0.3f}'.format(buy_rate), 
             '{0:0.3f}'.format(sell_rate), 
             get_window_profit(code, start_date, end_date, buy_rate, sell_rate))