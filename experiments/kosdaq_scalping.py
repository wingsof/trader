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

def get_ba_by_datetime(code, d, t):
    db = MongoClient(config.MONGO_SERVER)['stock']
    starttime = d.replace(hour = 8, minute = 30)
    endtime = d.replace(hour = 16, minute = 00)
    cursor = db[code + '_BA'].find({'date': {'$gte':starttime, '$lte': endtime}, '1': {'$eq': t}})
    last_data = list(cursor)[-1]
    return last_data['24'], last_data['23']  # wanna buy, wanna sell

def get_one_day_ba(d, code):
    db = MongoClient(config.MONGO_SERVER)['stock']
    starttime = d.replace(hour = 8, minute = 30)
    endtime = d.replace(hour = 16, minute = 00)
    cursor = db[code + '_BA'].find({'date': {'$gte':starttime, '$lte': endtime}})
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

def fetch_speed_data(code, d, df):
    start_time = df.iloc[0]['3']
    end_time = df.iloc[-1]['3']

    new_df = pd.DataFrame(columns=['time', 'price', 'buy_speed', 'sell_speed', 'buy_sum', 'sell_sum', 'buy_ba', 'sell_ba', 'up_cap', 'down_cap'])
    
    buy_sum = 0
    sell_sum = 0
    while start_time < end_time + 1:
        min_data = df[df['3'] == start_time]
        if len(min_data) == 0:
            start_time += 1
            continue
        buy_data = min_data[min_data['14'] == 49]
        sell_data = min_data[min_data['14'] == 50]

        buy_sum += buy_data['17'].sum()
        sell_sum += sell_data['17'].sum()

        buy_ba, sell_ba = get_ba_by_datetime(code, d, start_time)

        current = d.replace(hour = int(start_time / 100), minute = int(start_time % 100))
        new_df = new_df.append({'time':current,
                                'price':min_data.iloc[-1]['13'],
                                'buy_speed': buy_data['17'].sum(),
                                'sell_speed': sell_data['17'].sum(),
                                'buy_sum': buy_sum, 'sell_sum': sell_sum, 'buy_ba': buy_ba, 'sell_ba': sell_ba,
                                'up_cap': buy_ba / buy_data['17'].sum(), 'down_cap': sell_ba / sell_data['17'].sum(),
                                }, ignore_index=True)
        start_time += 1
    return new_df

if __name__ == '__main__':
    codes = list(get_bull_codes_by_date(startdate).values())
    codes = codes[2:]

    for code in codes:
        data = get_morning_prices(startdate, code)
        df = pd.DataFrame(data)
        is_tripple = check_tripple(df)

        if is_tripple:
            one_day_data = get_one_day_prices(startdate, code)
            one_day_ba = get_one_day_ba(startdate, code)
            one_day_df = pd.DataFrame(one_day_data)
            speeds = fetch_speed_data(code, startdate, one_day_df)
            #print(speeds[0], speeds[1])
            # wanna simple strategy calculating current buy_speed can go up to where and vice versa and calculating
            
            fig = plt.figure()
            fig.patch.set_facecolor('white')
            ax1 = fig.add_subplot(411, ylabel='price')
            ax2 = fig.add_subplot(412, ylabel='speed')
            ax3 = fig.add_subplot(413, ylabel='sum')
            ax4 = fig.add_subplot(414, ylabel='cap')
            speed_df = speeds[2]

            speed_df.plot(ax=ax1, x='time', y='price', color='r', lw=2.)
            speed_df.plot(ax=ax2, x='time', y=['buy_speed', 'sell_speed'])
            speed_df.plot(ax=ax3, x='time', y=['buy_sum', 'sell_sum'])
            speed_df.plot(ax=ax4, x='time', y=['up_cap', 'down_cap'])
            
            plt.show()
            
    #print(start_time)
        
        # data['13'] == prices