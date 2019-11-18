import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pymongo import MongoClient
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from dbapi import config

import matplotlib.pyplot as plt

# This is a first date can query kosdaq datas
# startdate = datetime(2019, 11, 11)

# first day for collecting
startdate = datetime(2019, 11, 18)
alpha_hour = 0 # 2019, 11, 14 수능날 추가 시간 필요

def get_bull_codes_by_date(d):
    db = MongoClient(config.MONGO_SERVER)['stock']

    starttime = d.replace(hour = 9, minute = 0)
    endtime = d.replace(hour = 9 + alpha_hour, minute = 10)
    cursor = db['KOSDAQ_BY_TRADED'].find({'date': {'$gte':starttime, '$lte': endtime}})
    return (list(cursor)[0])


def get_morning_prices(d, code):
    db = MongoClient(config.MONGO_SERVER)['stock']
    starttime = d.replace(hour = 8, minute = 30)
    endtime = d.replace(hour = 9 + alpha_hour, minute = 30)
    
    cursor = db[code].find({'date': {'$gte':starttime, '$lte': endtime}})
    return list(cursor)


def get_one_day_prices(d, code):
    db = MongoClient(config.MONGO_SERVER)['stock']
    starttime = d.replace(hour = 8, minute = 30)
    endtime = d.replace(hour = 16 + alpha_hour, minute = 00)
    
    cursor = db[code].find({'date': {'$gte':starttime, '$lte': endtime}})
    return list(cursor)


def get_ba_by_datetime(code, d, t):
    db = MongoClient(config.MONGO_SERVER)['stock']
    starttime = d.replace(hour = 8, minute = 30)
    endtime = d.replace(hour = 16, minute = 00)
    
    cursor = db[code + '_BA'].find({'date': {'$gte':starttime, '$lte': endtime}, '1': {'$eq': int(t)}})
    last_data = list(cursor)[-1]
     # wanna buy, wanna sell
    return last_data['24'], last_data['23'], last_data['6'] + last_data['10'] + last_data['14'] + last_data['18'] + last_data['22'], last_data['5'] + last_data['9'] + last_data['13'] + last_data['17'] + last_data['21']


def check_tripple(code, df):
    if len(df) == 0:
        return 0, False

    start_time = df.iloc[0]['3']

    tripple = True
    for i in range(3):
        min_data = df[df['3'] == start_time]
        if len(min_data) == 0:
            return 0, False
        # code argument is for testing purpose
        #print(min_data['13'].iloc[0], min_data['13'].iloc[-1])

        if i == 0:
            if min_data['13'].iloc[-1] - min_data['4'].iloc[0] < 0:
                tripple = False
        else:
            if min_data['13'].iloc[-1] - min_data['13'].iloc[0] < 0:
                tripple = False
        start_time += 1
    
    if tripple:
        while True:
            next_min = df[df['3'] == start_time]
            #print(code, start_time, len(next_min))
            if len(next_min) > 0:
                break
            start_time += 1
        print(code, (df.iloc[-1]['13'] - next_min.iloc[0]['13']) / next_min.iloc[0]['13'] * 100)

    return df.iloc[-1]['13'], tripple

def fetch_speed_data(code, d, df, price):
    start_time = df.iloc[0]['3']
    end_time = df.iloc[-1]['3']

    new_df = pd.DataFrame(columns=['time', 'price', 'buy_speed', 'sell_speed', 'buy_sum', 'sell_sum', 'buy_ba', 'sell_ba', 'buy_within_5', 'sell_within_5', 'up_cap', 'down_cap'])
    
    buy_sum = 0
    sell_sum = 0
    count = 0
    sell_price = 0
    while start_time < end_time + 1:
        min_data = df[df['3'] == start_time]
        if len(min_data) == 0:
            start_time += 1
            continue
        count += 1
        buy_data = min_data[min_data['14'] == 49]
        sell_data = min_data[min_data['14'] == 50]

        buy_sum += buy_data['17'].sum()
        sell_sum += sell_data['17'].sum()

        if count > 3 and sell_price == 0:
            if sell_sum > buy_sum:
                if count == 4:
                    sell_price = -1
                    print('DROP')
                    return None, -1
                else:
                    print(count, min_data.iloc[-1]['13'])
                    sell_price = min_data.iloc[-1]['13']
                    return None, sell_price

        buy_speed_ratio = 0
        sell_speed_ratio = 0

        buy_ba, sell_ba, buy_within_5, sell_within_5 = get_ba_by_datetime(code, d, start_time)

        if  buy_data['17'].sum() > 0:
            buy_speed_ratio = sell_within_5 / buy_data['17'].sum()
        if sell_data['17'].sum() > 0:
            sell_speed_ratio = buy_within_5 / sell_data['17'].sum()

        if buy_speed_ratio > 10:
            buy_speed_ratio = 10
        if sell_speed_ratio > 10:
            sell_speed_ratio = 10

        #print(start_time, min_data.iloc[-1]['13'], buy_within_5, sell_within_5, buy_speed_ratio, sell_speed_ratio)
        current = d.replace(hour = int(start_time / 100), minute = int(start_time % 100))
        new_df = new_df.append({'time':current,
                                'price':min_data.iloc[-1]['13'],
                                'buy_speed': buy_data['17'].sum(),
                                'sell_speed': sell_data['17'].sum(),
                                'buy_sum': buy_sum, 'sell_sum': sell_sum, 'buy_ba': buy_within_5, 'sell_ba': sell_within_5,
                                'up_cap': buy_speed_ratio, 'down_cap': sell_speed_ratio,
                                }, ignore_index=True)
        start_time += 1

    if sell_price == 0:
        sell_price = df.iloc[-1]['13']
    return new_df, sell_price

if __name__ == '__main__':
    bull_codes = get_bull_codes_by_date(startdate)
    bull_codes.pop('_id', None)
    bull_codes.pop('date', None)
    codes = list(bull_codes.values())

    for code in codes:
        data = get_morning_prices(startdate, code)
        df = pd.DataFrame(data)
        df = df[df['20'] == ord('2')]
        df = df[1:]
        
        price, is_tripple = check_tripple(code, df)

        if is_tripple:
            one_day_data = get_one_day_prices(startdate, code)
            
            one_day_df = pd.DataFrame(one_day_data)
            one_day_df = one_day_df[one_day_df['20'] == ord('2')]
            one_day_df = one_day_df[1:]
            

            speeds, sprice = fetch_speed_data(code, startdate, one_day_df, price)
            print(code, startdate, 'BUY Price', price, 'SELL Price', sprice)
            #print(speeds[0], speeds[1])
            # wanna simple strategy calculating current buy_speed can go up to where and vice versa and calculating
            """
            fig = plt.figure()
            fig.patch.set_facecolor('white')
            ax1 = fig.add_subplot(511, ylabel='price')
            ax2 = fig.add_subplot(512, ylabel='speed')
            ax3 = fig.add_subplot(513, ylabel='sum')
            ax4 = fig.add_subplot(514, ylabel='cap')
            ax5 = fig.add_subplot(515, ylabel='ba_size')
            #speed_df = speeds[2]

            speeds.plot(ax=ax1, x='time', y='price', color='r', lw=2.)
            speeds.plot(ax=ax2, x='time', y=['buy_speed', 'sell_speed'])
            speeds.plot(ax=ax3, x='time', y=['buy_sum', 'sell_sum'])
            speeds.plot(ax=ax4, x='time', y=['up_cap', 'down_cap'])
            speeds.plot(ax=ax5, x='time', y=['buy_ba', 'sell_ba'])
            plt.show()
            """
    #print(start_time)
        
        # data['13'] == prices
