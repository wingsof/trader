from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import date, timedelta, datetime
import gevent
import socket
import sys
import time
import threading
import pandas as pd
import numpy as np
from scipy.signal import find_peaks, peak_prominences
from pymongo import MongoClient
import itertools

from morning_server import message
from morning_server import stock_api
from morning_server import stream_readwriter
from morning.back_data import holidays
from morning.pipeline.converter import dt
from utils import time_converter
from configs import db


def reorder_pattern(p):
    pattern = p.copy()
    with_index = [[v, i] for i, v in enumerate(pattern)]
    with_index = sorted(with_index, key=lambda x: x[0])

    for i, wi in enumerate(with_index):
        pattern[wi[1]] = i + 1
    return pattern


def store_peak_statistics(sinfo):
    peak_db = MongoClient(db.HOME_MONGO_ADDRESS)['stock']
    query = {'plus': sinfo['plus'], 'type': sinfo['type'], 'height': sinfo['height']}
    db_data = list(peak_db['peak_statistics'].find(query))
    if len(db_data) == 0:
        peak_db['peak_statistics'].insert_one(sinfo)
    else:
        peak_db['peak_statistics'].delete_many(query)
        peak_db['peak_statistics'].insert_one(sinfo)


def find_pattern(is_plus, type_pattern, height_pattern):
    # Find yesterday close and today first peak and which peak first?
    peak_db_data = peak_db_plus if is_plus else peak_db_minus
    average_profit = []
    for peak_data in peak_db_data:
        data_type_pattern = [pd['type'] for pd in peak_data['peak']]
        data_height_pattern = [pd['height_order'] for pd in peak_data['peak']]
        height_len, type_len = len(height_pattern), len(type_pattern)

        if (len(data_height_pattern) + 1< height_len or
            len(data_type_pattern) + 1< type_len):
            continue

        target_type_pattern = data_type_pattern[:type_len]
        target_height_pattern = reorder_pattern(data_height_pattern[:height_len])

        if target_type_pattern == type_pattern and height_pattern == target_height_pattern:
            current_peak = peak_data['peak'][type_len-1]
            top_peaks = []
            for p in peak_data['peak'][type_len:]:
                if p['type'] == 1:
                    top_peaks.append(p)

                if len(top_peaks) == 2:
                    avg_peak_top_price = ((top_peaks[0]['price'] + top_peaks[1]['price']) / 2)
                    average_profit.append((avg_peak_top_price - current_peak['price']) / current_peak['price'] * 100.)
                    break
    return average_profit


peak_db = MongoClient(db.HOME_MONGO_ADDRESS)['stock']
peak_db_data = list(peak_db['peak_info'].find())
print('DB LEN', len(peak_db_data))
peak_db_plus = []
peak_db_minus = []
for pdd in peak_db_data:
    if len(pdd['peak']) == 0:
        continue

    if pdd['yesterday_close'] < pdd['peak'][0]['price']:
        peak_db_plus.append(pdd)
    else:
        peak_db_minus.append(pdd)

results = []
for i in range(2, 7):
    for h in itertools.permutations(range(1, i+1), i):
        for t in itertools.product(range(1, 3), repeat=(i-1)):
            yesterday_compare = [True, False]
            for is_plus in yesterday_compare:
                top_profits = find_pattern(is_plus, [0] + list(t), list(h))
                if len(top_profits) > 0:
                    top_profits = np.array(top_profits)
                    result = {'plus': is_plus, 'type': [0]+list(t), 'height': list(h), 
                                    'mean': np.array(top_profits).mean(), 'count': len(top_profits),
                                    'cv': (np.array(top_profits).std() / np.array(top_profits).mean() if np.array(top_profits).mean() != 0 else np.nan),
                                    'std': np.array(top_profits).std(),
                                    'good':  np.count_nonzero(top_profits > 0.25),
                                    'bad': np.count_nonzero(top_profits <= 0.25)}
                    store_peak_statistics(result)
                    results.append(result)

results = sorted(results, key=lambda x: x['mean'], reverse=True)
for r in results:
    print(r)
