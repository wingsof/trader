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
    return yesterday - timedelta(days=1), data


# use speculation to get past parameter to buy and sell
# get result profit for 1 year
def get_window_profit(code, start_date, end_date, cons):
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

        _, data = stock_chart.get_day_period_data(code, today, today)
        price_list = list(map(lambda x: {'high': x['3'], 'low': x['4'], 'close': x['5']}, data))
        if len(price_list) == 0:
            print('No data')
            today += timedelta(days=1)
            continue
        elif len(price_list) > 1:
            print('Something wrong', today)

        high_past = []
        low_past = []
        collecting = False
        yesterday = today - timedelta(days=1)
        while True:
            if len(high_past) == cons:
                collecting = True
                break

            yesterday, ydata = get_yesterday(yesterday)
            if ydata is None:
                break
            ylist = list(map(lambda x: {'high': x['3'], 'low': x['4'], 'close': x['5']}, ydata))[0]
            high_past.append(ylist['high'])
            low_past.append(ylist['low'])
            
        if not collecting:
            print('failed to get past data')
            continue

        low = price_list[0]['low']
        high = price_list[0]['high']
        close = price_list[0]['close']

        eighty_price = (max(high_past) - min(low_past)) * 0.8 + min(low_past)
        twenty_price = (max(high_past) - min(low_past)) * 0.2 + min(low_past)
        b_condition = eighty_price < high
        s_condition = twenty_price > low

        if bought['quantity'] != 0 and s_condition:
            money = close * bought['quantity']
            money -= money * 0.003
            bought['quantity'] = 0
        elif bought['quantity'] == 0 and b_condition and prev_close != 0:
            bought['quantity'] = money / close
            money = 0
            trade_count += 1

        if initial_price == 0:
            initial_price = close

        prev_close = close
        left = money if money != 0 else bought['quantity'] * prev_close
        
        yield today, left / initial_deposit * 100, close / initial_price * 100, trade_count
        print(today, 'P:', '{0:0.3f}'.format(left / initial_deposit * 100), '{0:0.3f}'.format(close / initial_price * 100), 'T:', trade_count, '80%:', eighty_price, '20%:', twenty_price, 'H:', high)
        today += timedelta(days=1)

#code_list = ['A005930']
code_list = [sys.argv[1]]
start_date = datetime(2015, 11, 1)
end_date = datetime(2018, 11, 29)

df = pd.DataFrame(columns=['code', 'date', 'profit', 'days', 'price'])

for code in code_list:
    for date, profit, p, tcount in get_window_profit(code, start_date, end_date, 20):
        df = df.append({'code': code, 'date': date, 'profit': profit, 'days': 20, 'price': p}, ignore_index=True)

#writer = pd.ExcelWriter(sys.argv[1] + '_updays.xlsx')
#df.to_excel(writer, 'Sheet1')
#writer.save()
