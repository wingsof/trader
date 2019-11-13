import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dbapi import stock_code, stock_chart
import pandas as pd
from datetime import datetime
from utils import time_converter

import matplotlib.pyplot as plt



# collect 2 year data and analyze flow
# 10등분으로 구분하여, 기관은 아래가 좋고, 개인은 위가 좋다
# 개인의 하락세 전환, 기관은 상승세 전환이 best
# 
if __name__ == '__main__':
    code_list = stock_code.get_kospi200_list()
    code_list = ['A005830']

    for code in code_list:
        df = pd.DataFrame(columns=['code', 'date', 'price', 'per', 'inst', 'foreign', 'foreign_hold'])
        df.set_index('date')

        count, data = stock_chart.get_day_period_data(code, datetime(2017, 1,1), datetime.now())
        current_foreign = data[0]['10'] # foreign, 12: inst
        per_total = 0
        data = data[1:]

        print(data[-2])
        print(data[-1])
        for d in data:
            today_foreign_vol = d['10'] - current_foreign
            today_inst_vol = d['12']
            today_all_vol = d['6']
            per_estimate =  -(today_inst_vol + today_foreign_vol)
            # TODO: 외부기관의 경우 잡히지 않는데, 이를 개인 매수세에서 잘라내는 방법 확인 필요
            per_total += per_estimate
            df = df.append({'code': code, 'date': time_converter.intdate_to_datetime(d['0']),
                            'price': d['5'], 'per': per_total,
                            'inst': d['13'], 'foreign': today_foreign_vol, 'foreign_hold': d['11']
                            }, ignore_index = True)
            current_foreign = d['10']

        fig = plt.figure()
        fig.patch.set_facecolor('white')
        ax1 = fig.add_subplot(411, ylabel='price')
        ax2 = fig.add_subplot(412, ylabel='per')
        ax3 = fig.add_subplot(413, ylabel='inst')
        ax4 = fig.add_subplot(414, ylabel='foreign')
        

        df.plot(ax=ax1, x='date', y='price', color='r')
        df.plot(ax=ax2, x='date', y='per')
        df.plot(ax=ax3, x='date', y='inst')
        df.plot(ax=ax4, x='date', y='foreign_hold')
        plt.show()
        """
        writer = pd.ExcelWriter(code + '_long.xlsx')
        df.to_excel(writer, 'Sheet1')
        writer.save()
        """