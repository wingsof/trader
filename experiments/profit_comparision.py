import fixed_rate_by_short as short_test
import fixed_rate_profit as normal_test
import fixed_rate_profit_sell_10 as normal_sell_test
import fixed_rate_left_profit as left_test

import numpy as np
from datetime import datetime, timedelta
import pandas as pd

# mean profit by date, drop index which has trade_count 0
# by each year, get buy_rate, sell_rate graph, color=method, size=profit


code = 'A005380'

start_date = datetime(2013, 1, 1)

buy_t_list = list(np.arange(0.01, 0.065, 0.005))
sell_t_list = list(np.arange(0.01, 0.065, 0.005))

func = [short_test.get_profit, normal_test.get_profit, normal_sell_test.get_profit, left_test.get_profit]
names = ['short', 'normal', 'normal_sell', 'left']

df = pd.DataFrame(columns=['date', 'profit', 'method', 'buy_rate', 'sell_rate', 'trade_count'])

while start_date < datetime.now():
    print('date', start_date)
    for buy_rate in buy_t_list:
        for sell_rate in sell_t_list:
            for i, f in enumerate(func):
                profit, trade_count = f(code, start_date, start_date + timedelta(days=365), buy_rate, sell_rate)
                df = df.append({'date': start_date + timedelta(days=365), 
                    'profit': profit, 'method': names[i], 'trade_count': trade_count, 'buy_rate': buy_rate, 'sell_rate': sell_rate}, ignore_index=True)
    start_date += timedelta(days=365)

    writer = pd.ExcelWriter(str(start_date.year) + str(start_date.month) + '.xlsx')
    df.to_excel(writer, 'Sheet1')
    writer.save()


writer = pd.ExcelWriter('method_comparision.xlsx')
df.to_excel(writer, 'Sheet1')
writer.save()
