# get speculation from 2018. 10. 22 and get real profit
# compare expectation and real profit

from utils import speculation, profit_calc
from dbapi import stock_code, stock_chart
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

code_list = stock_code.get_kospi200_list()

start_date = datetime(2018, 10, 22)

s = speculation.Speculation()
sp_list = s.get_speculation(start_date, code_list)

df = pd.DataFrame(sp_list)

n = datetime.now()
df['real_profit'] = np.zeros(len(df))

for code in code_list:
    _, data = stock_chart.get_day_period_data(code, start_date+timedelta(days=1), datetime.now())
    price_list = list(map(lambda x: {'high': x['3'], 'low': x['4'], 'close': x['5']}, data))

    buy_rate = df[df['code'] == code].iloc[0]['buy_rate']
    sell_rate = df[df['code'] == code].iloc[0]['sell_rate']

    profit, _ = profit_calc.get_avg_profit_by_day_data(pd.DataFrame(price_list), buy_rate, sell_rate)
    df.loc[df['code'] == code, 'real_profit'] = profit


print(df[df['profit_expected'] > 105]['real_profit'].mean())

