import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from utils import speculation, profit_calc
from dbapi import stock_code, stock_chart
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import statistics

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
    return yesterday - timedelta(days=1), data


def get_tomorrow(tomorrow):
    max_depth = 10
    while True:
        if max_depth <= 0:
            return None, None

        l, data = stock_chart.get_day_period_data(code, tomorrow, tomorrow + timedelta(days=1))
        if l == 0:
            tomorrow = tomorrow + timedelta(days=1)
            max_depth -= 1
        else: break
    return tomorrow + timedelta(days=1), data


def get_today_profit(code, today, data, per):
    today_result = list(map(lambda x: {'high': x['3'], 'low': x['4'], 'close': x['5']}, data))[0]

    yesterday, ydata = get_yesterday(today - timedelta(days=1))
    if ydata is None:
        return None

    y_result = list(map(lambda x: {'high': x['3'], 'low': x['4'], 'close': x['5']}, ydata))[0]
    """
    print(aa, dy_result['close'])
    print(yesterday, y_result['close'])
    print(today, (y_result['close'] - dy_result['close']) / dy_result['close'] * 100)
    """
    if per - 0.5 <= (today_result['close'] - y_result['close']) / y_result['close'] * 100 <= per + 0.5:
        future_close = []
        tomorrow = today + timedelta(days=1)
        while True:
            if len(future_close) == 5:
                break

            #print(tomorrow)
            tomorrow, tdata = get_tomorrow(tomorrow)
            if tdata is None:
                return None

            result = list(map(lambda x: {'high': x['3'], 'low': x['4'], 'close': x['5']}, tdata))[0]
            future_close.append(result['close'])
            
        profit = (statistics.mean(future_close) - today_result['close']) / today_result['close'] * 100
        print(code, today.year, today.month, today.day, per, '{0:0.3f}'.format(profit), future_close)
        return profit
        #print(today, '\t{0:0.2f}'.format(today_max), '\t{0:0.2f}'.format(today_low), '\t{0:0.2f}'.format(today_close))

    return None
    #print(today)

if __name__ == '__main__':
    code_list = stock_code.get_kospi200_list()
    df = pd.DataFrame(columns=['code', 'date', 'low', 'max', 'close'])
    for code in code_list:
        today = datetime(2015, 1, 1)
        while datetime.now() > today:
            l, data = stock_chart.get_day_period_data(code, today, today + timedelta(days=1))
            if l == 0: 
                today += timedelta(days=1)
                continue
            else:
                for i in range(-5, 6):
                    r = get_today_profit(code, today, data, i)
                    if r is not None:
                        df = df.append({'code': code, 'date': today, 'profit':i, 'mean':r, }, ignore_index=True)

            today += timedelta(days=1)

writer = pd.ExcelWriter('oneweek_after_profit.xlsx')
df.to_excel(writer, 'Sheet1')
writer.save()
