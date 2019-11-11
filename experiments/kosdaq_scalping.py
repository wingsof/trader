import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pymongo import MongoClient
from datetime import datetime, timedelta
import pandas as pd

from dbapi import config

import matplotlib.pyplot as plt

# This is a first date can query kosdaq datas
# startdate = datetime(2019, 11, 11)

# first day for collecting
startdate = datetime(2019, 11, 11)

def get_bull_codes_by_date(d):
    db = MongoClient(config.MONGO_SERVER)['stock']

    starttime = d.replace(hour = 9, minute = 0)
    endtime = d.replace(hour = 9, minute = 10)
    cursor = db['KOSDAQ_BY_TRADED'].find({'date': {'$gte':starttime, '$lte': endtime}})
    return (list(cursor)[0])

def get_morning_prices(d, code):
    db = MongoClient(config.MONGO_SERVER)['stock']
    starttime = d.replace(hour = 9, minute = 0)
    endtime = d.replace(hour = 9, minute = 10)
    
    cursor = db[code].find({'date': {'$gte':starttime, '$lte': endtime}})
    return list(cursor)

def get_one_day_prices(d, code):
    db = MongoClient(config.MONGO_SERVER)['stock']
    starttime = d.replace(hour = 8, minute = 30)
    endtime = d.replace(hour = 16, minute = 00)
    
    cursor = db[code].find({'date': {'$gte':starttime, '$lte': endtime}})
    return list(cursor)

def check_tripple(df):
    start_time = df.iloc[0]['3']

    tripple = True
    for i in range(3):
        min_data = df[df['3'] == start_time]
        #print(min_data['13'].iloc[0], min_data['13'].iloc[-1])

        if i == 0:
            if min_data['13'].iloc[-1] - min_data['4'].iloc[0] < 0:
                tripple = False
        else:
            if min_data['13'].iloc[-1] - min_data['13'].iloc[0] < 0:
                tripple = False
        start_time += 1
    
    next_min = df[df['3'] == start_time]
    if tripple:
        print(code, (df.iloc[-1]['13'] - next_min.iloc[0]['13']) / next_min.iloc[0]['13'] * 100)

    return tripple

def fetch_speed_data(d, df):
    start_time = df.iloc[0]['3']
    end_time = df.iloc[-1]['3']

    buy_speeds = []
    sell_speeds = []
    new_df = pd.DataFrame(columns=['time', 'price', 'buy_speed', 'sell_speed'])
    
    buy_sum = 0
    sell_sum = 0
    while start_time < end_time + 1:
        min_data = df[df['3'] == start_time]
        if len(min_data) == 0:
            start_time += 1
            continue
        buy_data = min_data[min_data['14'] == 49]
        sell_data = min_data[min_data['14'] == 50]
        buy_speeds.append(buy_data['17'].sum())
        sell_speeds.append(sell_data['17'].sum())

        buy_sum += buy_data['17'].sum()
        sell_sum += sell_data['17'].sum()
        
        current = d.replace(hour = int(start_time / 100), minute = int(start_time % 100))
        new_df = new_df.append({'time':current,
                                'price':min_data.iloc[-1]['13'],
                                'buy_speed': buy_data['17'].sum(),
                                'sell_speed': sell_data['17'].sum(),
                                'buy_sum': buy_sum, 'sell_sum': sell_sum,
                                }, ignore_index=True)
        start_time += 1
    return buy_speeds, sell_speeds, new_df

if __name__ == '__main__':
    codes = list(get_bull_codes_by_date(startdate).values())
    codes = codes[2:]

    for code in codes:
        data = get_morning_prices(startdate, code)
        df = pd.DataFrame(data)
        is_tripple = check_tripple(df)

        if is_tripple:
            one_day_data = get_one_day_prices(startdate, code)
            one_day_df = pd.DataFrame(one_day_data)
            speeds = fetch_speed_data(startdate, one_day_df)
            #print(speeds[0], speeds[1])
            fig = plt.figure()
            fig.patch.set_facecolor('white')
            ax1 = fig.add_subplot(311, ylabel='price')
            ax2 = fig.add_subplot(312, ylabel='speed')
            ax3 = fig.add_subplot(313, ylabel='sum')
            speed_df = speeds[2]

            speed_df.plot(ax=ax1, x='time', y='price', color='r', lw=2.)
            speed_df.plot(ax=ax2, x='time', y=['buy_speed', 'sell_speed'])
            speed_df.plot(ax=ax3, x='time', y=['buy_sum', 'sell_sum'])
            
            plt.show()
            
    #print(start_time)
        
        # data['13'] == prices