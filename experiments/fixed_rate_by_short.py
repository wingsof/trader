# get speculation from 2018. 10. 22 and get real profit
# compare expectation and real profit
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from utils import speculation, profit_calc
from dbapi import stock_code, stock_chart
import pandas as pd
from datetime import datetime, timedelta
import numpy as np


def get_profit(code, start_date, end_date, buy_rate, sell_rate):
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

        if bought['quantity'] is not 0 and high >= prev_close + buy_threshold:
            money = (bought['price'] - close) * bought['quantity'] + bought['balance']
            money -= money * 0.003
            bought['quantity'] = 0
        elif bought['quantity'] is 0 and prev_close != 0 and low <= prev_close - sell_threshold:
            bought['quantity'] = money / close
            bought['price'] = close
            bought['balance'] = money
            money = 0
            trade_count += 1


        prev_close = close

    left = money if money is not 0 else (bought['price'] - prev_close) * bought['quantity'] + bought['balance']
    return (left / initial_deposit * 100, trade_count)


if __name__ == '__main__':
    code = 'A005930'

    start_date = datetime(2016, 1, 1)
    end_date = datetime(2017, 1, 1)

    buy_t_list = list(np.arange(0.01, 0.065, 0.005))
    sell_t_list = list(np.arange(0.01, 0.065, 0.005))


    for buy_rate in buy_t_list:
        for sell_rate in sell_t_list:
            print('{0:0.3f}'.format(buy_rate), 
                 '{0:0.3f}'.format(sell_rate), 
                 get_profit(code, start_date, end_date, buy_rate, sell_rate))
