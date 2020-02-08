from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import date, timedelta

from morning_server import stock_api
from utils import time_converter
from morning.pipeline.converter import dt


# be careful, today is just for printing today, just use past data

def get_past_volume_average(past_time_data, t):
    volumes = []
    for ptd in past_time_data:
        volume = 0
        for min_d in ptd:
            if min_d['time'] > t:
                break
            volume += min_d['volume']
        volumes.append(volume)
    if len(volumes) == 0:
        return 0

    return sum(volumes) / len(volumes)


def get_yesterday_volume(ydata, t):
    volume = 0
    for data in ydata:
        if data['time'] > t:
            break
        volume += data['volume']
    return volume

def same_time_over_volume(reader, code_dict):
    for progress, (code, v) in enumerate(code_dict.items()): 
        today_min_data = v['today_min_data'] 
        yesterday_min_data = v['past_min_data'][-1]
        volume = sum([d['volume'] for d in today_min_data[:3]])
        highest = max([d['highest_price'] for d in today_min_data[:3]])
        highest_volume = max([d['volume'] for d in today_min_data[:3]])
        for tmd in today_min_data[3:]:
            volume += tmd['volume']
            yvolume = get_yesterday_volume(yesterday_min_data, tmd['time'])
            pvolume = get_past_volume_average(v['past_min_data'], tmd['time'])
            if highest_volume < tmd['volume']:
                highest_volume = tmd['volume']

            if yvolume == 0 or pvolume == 0:
                continue
            elif tmd['close_price'] < v['yesterday_close']:
                continue
            elif tmd['close_price'] < today_min_data[0]['start_price']:
                continue
            elif abs((tmd['highest_price'] - tmd['lowest_price']) / tmd['lowest_price'] * 100) >= 4:
                break

            #print(tmd['time'], highest, 'high', tmd['highest_price'], 'close', tmd['close_price'], 'start', tmd['start_price'])
            if volume > yvolume * 3 and volume > pvolume * 6.5 and volume * tmd['close_price'] >= 100000000 and tmd['close_price'] > highest and tmd['start_price'] < tmd['close_price'] and tmd['volume'] < highest_volume:
                v['time'] = tmd['time'] 
                v['amount'] = volume * tmd['close_price']
                v['until_now_profit'] = (tmd['close_price'] - today_min_data[0]['start_price']) / today_min_data[0]['start_price'] * 100
                break
            
            if tmd['highest_price'] > highest:
                highest = tmd['highest_price']

    candidates = []
    for code, v in code_dict.items():
        if v['time'] != 0:
            candidates.append(code)
    return candidates
