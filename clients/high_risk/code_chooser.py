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

def same_time_over_volume(reader, code_dict):
    for progress, (code, v) in enumerate(code_dict.items()): 
        today_min_data = v['today_min_data'] 
        volume = sum([d['volume'] for d in today_min_data[:3]])
        for tmd in today_min_data[3:]:
            volume += tmd['volume']
            if tmd['close_price'] < v['yesterday_close']:
                continue

            avg_volume = get_past_volume_average(v['past_min_data'], tmd['time'])
            if avg_volume == 0:
                continue
            elif volume > avg_volume * 6.5:
                print('Found', code, tmd['time'])
                v['time'] = tmd['time']
                break

    candidates = []
    for code, v in code_dict.items():
        if v['time'] != 0:
            candidates.append(code)
    return candidates
