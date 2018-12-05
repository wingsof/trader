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


if __name__ == '__main__':
    #code = 'A005380'
    """
    import sys
    if len(sys.argv) < 2:
        print('input the code')
        sys.exit(1)
    """

    start_year = 2015
    #buy_t_list = list(np.arange(0.01, 0.065, 0.005))
    #sell_t_list = list(np.arange(0.01, 0.065, 0.005))
    buy_t_list = [0.02, 0.03, 0.04]
    sell_t_list = [0.02, 0.03, 0.04]
    code_list = stock_code.get_kospi200_list()
    df = pd.DataFrame(columns=['year', 'code', 'buy_rate', 'sell_rate', 'profit', 'trade_count'])
    while True:
        start_date = datetime(start_year, 1, 1)
        for buy_rate in buy_t_list:
            for sell_rate in sell_t_list:
                for code in code_list:
                    profit, count = get_profit(code, start_date, start_date + timedelta(days=365), buy_rate, sell_rate)
                    df = df.append({'year': start_date.year, 'code': code, 'buy_rate': buy_rate, 'sell_rate': sell_rate, 'profit': profit, 'count': count}, ignore_index=True)
                    """
                    print(start_date.year, '{0:0.3f}'.format(buy_rate), 
                         '{0:0.3f}'.format(sell_rate), 
                         get_profit(sys.argv[1], start_date, start_date + timedelta(days=365), buy_rate, sell_rate))
                    """
        start_year += 1
        if datetime(start_year, 1, 1) > datetime.now():
            break

    
    writer = pd.ExcelWriter('right_result.xlsx')
    df.to_excel(writer, 'Sheet1')
    writer.save()
