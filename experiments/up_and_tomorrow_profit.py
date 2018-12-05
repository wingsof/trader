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

def get_yesterday(yesterday):
    max_depth = 10
    while True:
        if max_depth <= 0:
            return None, None

        l, data = stock_chart.get_day_period_data(code, yesterday, yesterday + timedelta(days=1))
        if l == 0:
            yesterday = yesterday - timedelta(days=1)
            max_depth -= 1
        else: break
    return yesterday, data

def get_today_profit(code, today, data):
    today_result = list(map(lambda x: {'high': x['3'], 'low': x['4'], 'close': x['5']}, data))[0]

    yesterday, ydata = get_yesterday(today - timedelta(days=1))
    if ydata is None:
        return None

    aa, bydata = get_yesterday(yesterday - timedelta(days=1))
    y_result = list(map(lambda x: {'high': x['3'], 'low': x['4'], 'close': x['5']}, ydata))[0]
    dy_result = list(map(lambda x: {'high': x['3'], 'low': x['4'], 'close': x['5']}, bydata))[0]
    """
    print(aa, dy_result['close'])
    print(yesterday, y_result['close'])
    print(today, (y_result['close'] - dy_result['close']) / dy_result['close'] * 100)
    """
    if (y_result['close'] - dy_result['close']) / dy_result['close'] * 100 >= 3:
        today_max = (today_result['high'] - y_result['close']) / y_result['close'] * 100
        today_low = (today_result['low'] - y_result['close']) / y_result['close'] * 100
        today_close = (today_result['close'] - y_result['close']) / y_result['close'] * 100
        return today_low, today_max, today_close
        print(today, '\t{0:0.2f}'.format(today_max), '\t{0:0.2f}'.format(today_low), '\t{0:0.2f}'.format(today_close))

    return None
    #print(today)

if __name__ == '__main__':
    code_list = stock_code.get_kospi200_list()
    df = pd.DataFrame(columns=['code', 'date', 'low', 'max', 'close'])
    for code in code_list:
        today = datetime(2015, 1, 1)
        test = 10 
        while datetime.now() > today:
            l, data = stock_chart.get_day_period_data(code, today, today + timedelta(days=1))
            if l == 0: 
                today += timedelta(days=1)
                continue
            else:
                r = get_today_profit(code, today, data)
                if r is not None:
                    df = df.append({'code': code, 'date': today, 'low':r[0], 'max':r[1], 'close':r[2]}, ignore_index=True)

            today += timedelta(days=1)
            if test == 0:
                test -= 1
                break

writer = pd.ExcelWriter('tommorows_after_3per.xlsx')
df.to_excel(writer, 'Sheet1')
writer.save()
