# get speculation from 2018. 10. 22 and get real profit
# compare expectation and real profit

from utils import speculation, profit_calc
from dbapi import stock_code, stock_chart
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

code_list = stock_code.get_kospi200_list()

start_date = datetime(2017, 1, 1)
end_date = start_date + timedelta(days=30)
n = datetime.now()

result_df = pd.DataFrame(columns=['date', 'mean'])

no_past_codes = []
for code in code_list:
    l, d = stock_chart.get_day_period_data(code, start_date - timedelta(days=30), start_date)
    if l is 0:
        no_past_codes.append(code)

for code in no_past_codes:
    code_list.remove(code)


while n > end_date:
    start_date += timedelta(days=1)
    end_date = start_date + timedelta(days=30)

    s = speculation.Speculation()
    # exception: current kospi 200 code does have past data
    sp_list = s.get_speculation(start_date, code_list, True)
    df = pd.DataFrame(sp_list)

    for code in code_list:
        _, data = stock_chart.get_day_period_data(code, start_date, end_date)
        price_list = list(map(lambda x: {'high': x['3'], 'low': x['4'], 'close': x['5']}, data))

        buy_rate = df[df['code'] == code].iloc[0]['buy_rate']
        sell_rate = df[df['code'] == code].iloc[0]['sell_rate']

        profit, _ = profit_calc.get_avg_short_profit_by_day_data(pd.DataFrame(price_list), buy_rate, sell_rate)
        df.loc[df['code'] == code, 'real_profit'] = profit

    mean_v = df[df['profit_expected'] > 105]['real_profit'].mean()
    result_df.append({'date':start_date, 'mean': mean_v}, ignore_index=True)

result_df = result_df.set_index('date')
writer = pd.ExcelWriter('short.xlsx')
result_df.to_excel(writer,'Sheet1')
writer.save()
