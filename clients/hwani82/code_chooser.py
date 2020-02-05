from sklearn.linear_model import LinearRegression
import numpy as np

from morning_server import stock_api
from utils import time_converter
from morning.pipeline.converter import dt


# be careful, today is just for printing today, just use past data

def positive_slope(reader, today, code_dict):
    candidates = []
    for progress, (code, v) in enumerate(code_dict.items()):
        print('positive slope', today, f'{progress+1}/{len(code_dict)}', end='\r')
        past_data = v['past_data']
        last_mavg = [d['moving_average'] for d in past_data[-10:]]
        X = np.arange(len(last_mavg)).reshape((-1,1))
        reg = LinearRegression().fit(X, np.array(last_mavg))
        if reg.coef_[0] > 0:
            candidates.append(code)
    print('')
    return candidates


def positive_cum_volume(reader, today, code_dict):
    candidates = []
    cum_buy_codes = []
    for progress, (code, v) in enumerate(code_dict.items()):
        print('positive cum volume', today, f'{progress+1}/{len(code_dict)}', end='\r')
        past_data = v['past_data']
        yesterday_data = past_data[-1]

        if yesterday_data['cum_buy_volume'] > yesterday_data['cum_sell_volume']:
            candidates.append(code)
    print('')
    return candidates


def positive_yesterday_close_over_mavg(reader, today, code_dict):
    candidates = []
    for progress, (code, v) in enumerate(code_dict.items()):
        print('positive yesterday close', today, f'{progress+1}/{len(code_dict)}', end='\r')
        past_data = v['past_data']
        yesterday_data = past_data[-1]

        if yesterday_data['moving_average'] > yesterday_data['close_price']:
            candidates.append(code)
    print('')
    return candidates


def higher_yesterday_amount(reader, today, code_dict):
    candidates = []
    for progress, (code, v) in enumerate(code_dict.items()):
        print('higher yesterday amount', today, f'{progress+1}/{len(code_dict)}', end='\r')
        past_data = v['past_data']
        yesterday_data = past_data[-1]
        candidates.append({'code': code, 'amount': yesterday_data['amount']})
    candidates = sorted(candidates, key=lambda x: x['amount'], reverse=True)
    candidates = candidates[:150]
    print('')
    return [d['code'] for d in candidates]


def negative_individual_investor(reader, today, code_dict):
    #check 5 days
    candidates = []
    for progress, (code, v) in enumerate(code_dict.items()):
        print('investor', today, f'{progress+1}/{len(code_dict)}', end='\r')
        investor_data = stock_api.request_investor_data(reader, code, 150)
        print(investor_data[-5:])
        today_int = v['past_data'][-1]['0']
        find_index = -1
        for i, inv in enumerate(investor_data):
            if inv['0'] == today_int:
                find_index = i
                break
        if find_index == -1:
            continue

        volume_array = []
        current_volume = 0
        for v in investor_data[:find_index+1]:
            data = dt.cybos_stock_investor_convert(v)
            current_volume += data['individual']
            volume_array.append(current_volume)
        volume_array = volume_array[-5:] # check 5 days
        print('volume', volume_array)
        X = np.arange(len(volume_array)).reshape((-1,1))
        reg = LinearRegression().fit(X, np.array(volume_array))
        print('slope', reg.coef_[0])
        if reg.coef_[0] < 0:
            candidates.append(code)
    return candidates
