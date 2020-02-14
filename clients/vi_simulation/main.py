from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))


from clients.common import morning_client
from datetime import datetime, date, timedelta
from morning.back_data import holidays
from morning_server import stock_api
import gevent
from gevent.queue import Queue
from clients.vi_follower import stock_follower
from configs import db
from pymongo import MongoClient
from morning.pipeline.converter import dt
import numpy as np
from scipy.signal import find_peaks, peak_prominences


target_date = datetime(2020, 2, 14)
code_dict = dict()
STATE_NONE = 0
STATE_BOTTOM_PEAK = 1
STATE_BUY = 1

def get_reversed(s):
    distance_from_mean = s.mean() - s
    return distance_from_mean + s.mean()


def calculate(x):
    peaks, _ = find_peaks(x, distance=10)
    prominences = peak_prominences(x, peaks)[0]

    peaks = np.extract(prominences > x.mean() * 0.002, peaks)
    prominences = np.extract(prominences > x.mean() * 0.002, prominences)
    return peaks, prominences


def get_peaks(avg_data, is_top):
    if not is_top:
        prices = get_reversed(avg_data)
    else:
        prices = avg_data
    peaks, _ = calculate(prices)
    return peaks


def get_avg_price(price_array):
    if len(price_array) < 10:
        return []
    avg_prices = np.array([])
    result_prices = []
    for p in price_array:
        avg_prices = np.append(avg_prices, np.array([p]))

        if len(avg_prices) == 10:
            result_prices.append(avg_prices.mean())
            avg_prices = avg_prices[1:]
        else:
            result_prices.append(avg_prices.mean())
    return np.array(result_prices)


def get_tick_data(code, today, t):
    print('get_tick_data', code, today, t)
    # TODO: no date field 2020/2/14 in db
    tick_data = db_collection[code].find({'18': {'$gt': t}})
    converted_data = []
    for td in tick_data:
        converted = dt.cybos_stock_tick_convert(td)
        converted_data.append(converted)
    return converted_data


def get_past_datas(code, today, yesterday, t):
    data = morning_client.get_past_day_data(code, yesterday, yesterday)
    if len(data) != 1:
        print('Cannot get yesterday data', code, yesterday)
        return
    code_dict[code]['yesterday_data'] = data[0]
    min_data = morning_client.get_minute_data(code, today, today, int(t / 100))
    code_dict[code]['today_min_data'] = min_data
    code_dict[code]['today_tick_data'] = get_tick_data(code, today, t)
    for mdata in code_dict[code]['today_min_data']:
        if mdata['highest_price'] > code_dict[code]['vi_highest']:
            code_dict[code]['vi_highest'] = mdata['highest_price']


def get_min_data(tick, current):
    min_data = None
    if tick['time'] != current['tick_min']:
        if current['tick_min'] == 0:
            current['tick_min'] = tick['time']
        else:
            if len(current['prices']) > 0:
                min_data = {'h': max(current['prices']),
                            'l': min(current['prices']),
                            'o': current['prices'][0],
                            'c': current['prices'][-1],
                            'time': current['tick_min'],
                            'volume': sum(current['volumes'])}

            current['prices'].clear()
            current['volumes'].clear()

    current['prices'].append(tick['current_price'])
    current['volumes'].append(tick['volume'])
    current['tick_min'] = tick['time']
    return min_data


def start_trade(code, t):
    if len(code_dict[code]['today_tick_data']) == 0:
        print('something goes wrong', code)
    elif code_dict[code]['yesterday_data']['close_price'] > code_dict[code]['today_tick_data'][0]['current_price']:
        print('Low price than yesterday', code)
        return 
    
    current = {'tick_min': 0, 'prices': [], 'volumes': [], 'cum_buy_volumes': [], 'cum_sell_volumes': []}
    for tick in code_dict[code]['today_tick_data']:
        if tick['market_type'] == dt.MarketType.IN_MARKET:
            min_data = get_min_data(tick, current)
            if min_data is not None:
                code_dict[code]['today_min_data'].append({
                    'code': code, 'time': min_data['time'],
                    'start_price': min_data['o'], 'close_price': min_data['c'],
                    'highest_price': min_data['h'], 'lowest_price': min_data['l'],
                    'volume': min_data['volume']})

            if code_dict[code]['state'] == STATE_NONE:
                avg_prices = get_avg_price([d['close_price'] for d in code_dict[code]['today_min_data']])
                if len(avg_prices) > 0:
                    peaks = get_peaks(avg_prices, False)
                    if len(peaks) > 0:
                        for p in peaks:
                            data = code_dict[code]['today_min_data'][p]
                            if data['time'] > (t / 100) and data['close_price'] < code_dict[code]['vi_highest']:
                                code_dict[code]['bottom_price'] = data['close_price']
                                code_dict[code]['state'] = STATE_BOTTOM_PEAK
            elif code_dict[code]['state'] == STATE_BOTTOM_PEAK:
                if tick['current_price'] > code_dict[code]['vi_highest']:
                    code_dict[code]['buy_price'] = tick['current_price']
                    gap_price = (code_dict[code]['vi_highest'] - code_dict[code]['bottom_price']) * 2/3
                    code_dict[code]['target_gap'] = gap_price
            elif code_dict[code]['state'] == STATE_BUY:
                if tick['current_price'] > code_dict[code]['vi_highest'] + code_dict[code]['target_gap']:
                    print('OK')
                    break
                elif tick['current_price'] < code_dict[code]['vi_highest'] - code_dict[code]['target_gap']:
                    print('FAILED')
                    break


if __name__ == '__main__':
    db_collection = MongoClient(db.HOME_MONGO_ADDRESS).trade_alarm
    alarm_data = list(db_collection['alarm'].find({'date': {'$gte': target_date, '$lte': target_date + timedelta(days=1)}}))
    alarm_data = sorted(alarm_data, key=lambda x: x['date'])
    market_code = morning_client.get_market_code()
    yesterday = holidays.get_yesterday(target_date.date())

    for code in market_code:
        code_dict[code] = {'state': STATE_NONE, 'yesterday_data': None, 'today_min_data': None, 'vi': True, 'today_tick_data': None, 'vi_highest': 0, 'bottom_price': 0, 'buy_price': 0, 'target_gap': 0}

    for adata in alarm_data:
        #print(adata)
        code = adata['3']
        alarm_type = adata['1']
        market_type = adata['2']
        vi_type = adata['4']
        if alarm_type == ord('1') and market_type == 201 and vi_type == 755:
            if code_dict[code]['yesterday_data'] is None: #prevent 2nd
                print('get past data', code, adata['0'])
                get_past_datas(code, target_date.date(), yesterday, adata['0']) 
        elif alarm_type == ord('1') and market_type == 201 and vi_type == 756:
            if code_dict[code]['yesterday_data'] is not None:
                print('start trade', code, adata['0'])
                start_trade(code, adata['0'])
