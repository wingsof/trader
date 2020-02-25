from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))


from clients.common import morning_client
from datetime import datetime, date, timedelta, time
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
import pandas as pd


STATE_NONE = 0
STATE_BOTTOM_PEAK = 1
STATE_BUY = 2

SUCCESS = 3
FAIL = 2
HOLDING = 1
NONE = 0

def get_reversed(s):
    distance_from_mean = s.mean() - s
    return distance_from_mean + s.mean()


def calculate(x):
    peaks, _ = find_peaks(x, distance=10)
    prominences = peak_prominences(x, peaks)[0]

    peaks = np.extract(prominences > x.mean() * 0.015, peaks)
    prominences = np.extract(prominences > x.mean() * 0.015, prominences)
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


def get_past_datas(code, today, t, code_dict):
    yesterday = holidays.get_yesterday(today)
    data = morning_client.get_past_day_data(code, yesterday, yesterday)
    if len(data) != 1:
        print('Cannot get yesterday data', code, yesterday)
        return
    code_dict[code]['yesterday_data'] = data[0]
    min_data = morning_client.get_minute_data(code, today, today)
    hour = int(t / 10000)
    minute = int((t % 10000) / 100)
    vi_datetime = datetime.combine(today, time(hour, minute))
    before_vi_datetime = vi_datetime - timedelta(seconds=60)
    after_vi_datetime = vi_datetime + timedelta(seconds=120)

    before_datas = []
    after_datas = []
    for mdata in min_data:
        if mdata['time'] <= before_vi_datetime.hour * 100 + before_vi_datetime.minute:
            before_datas.append(mdata)
        elif mdata['time'] >= after_vi_datetime.hour * 100 + after_vi_datetime.minute:
            after_datas.append(mdata)

    code_dict[code]['today_min_data'] = before_datas
    code_dict[code]['today_min_after_vi'] = after_datas[:-1]
    for mdata in code_dict[code]['today_min_data']:
        if mdata['highest_price'] > code_dict[code]['vi_highest']:
            code_dict[code]['vi_highest'] = mdata['highest_price']
    """
    if code_dict[code]['vi_highest'] == 0:
        # Temporary when 9:00 starts VI then no today_min_data
        code_dict[code]['vi_highest'] = code_dict[code]['today_min_after_vi'][0]['start_price']#code_dict[code]['yesterday_data']['close_price'] * 1.1
    """

def debug_print(*kargs):
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        print(kargs)


def start_trade(code, t, code_dict):
    if len(code_dict[code]['today_min_data']) > 0 and code_dict[code]['yesterday_data']['close_price'] > code_dict[code]['today_min_data'][-1]['close_price']:
        print('Low price than yesterday', code)
        return 
    
    current = {'tick_min': 0, 'prices': [], 'volumes': [], 'cum_buy_volumes': [], 'cum_sell_volumes': []}
    vi_price = 0
    bottom_margin = 0

    for tm in code_dict[code]['today_min_after_vi']:
        if vi_price == 0:
            vi_price = tm['start_price']

        min_data = tm
        code_dict[code]['today_min_data'].append(min_data)

        if code_dict[code]['state'] == STATE_NONE:
            if tm['highest_price'] > code_dict[code]['vi_highest']:
                code_dict[code]['vi_highest'] = tm['highest_price']
            debug_print(code, min_data['time'], 'STATE NONE')
            avg_prices = get_avg_price([d['close_price'] for d in code_dict[code]['today_min_data']])
            if len(avg_prices) > 0:
                peaks = get_peaks(avg_prices, False)
                debug_print(code, min_data['time'], 'len', len(peaks), [code_dict[code]['today_min_data'][p]['time'] for p in peaks])
                if len(peaks) > 0:
                    for p in peaks:
                        data = code_dict[code]['today_min_data'][p]
                        debug_print('peak', 'min close', data['close_price'], 'vi', code_dict[code]['vi_highest'])
                        if data['time'] > (t / 100) and data['close_price'] < vi_price:
                            code_dict[code]['bottom_price'] = data['close_price']
                            code_dict[code]['state'] = STATE_BOTTOM_PEAK
                            print('bottom price', data['close_price'], 'time', data['time'], 'VI Highest', code_dict[code]['vi_highest'])
                            #print('avg prices', tm['time'], avg_prices)
                            #sys.exit(0)
        elif code_dict[code]['state'] == STATE_BOTTOM_PEAK:
            debug_print(code, min_data['time'], 'STATE BOTTOM PEAK', min_data['highest_price'], code_dict[code]['vi_highest'])
            if min_data['highest_price'] > code_dict[code]['vi_highest'] and tm['time'] <= 1500:
                code_dict[code]['buy_price'] = code_dict[code]['vi_highest']
                gap_price = (code_dict[code]['vi_highest'] - code_dict[code]['bottom_price']) * 2/3
                code_dict[code]['target_gap'] = gap_price

                if gap_price / code_dict[code]['vi_highest'] * 100 > 1:
                    current_profit = (code_dict[code]['buy_price'] - code_dict[code]['yesterday_data']['close_price']) / code_dict[code]['yesterday_data']['close_price'] * 100
                    if current_profit > 20:
                        print(code, 'current price is over 20 dropped', 'time', tm['time'])
                        break
                    code_dict[code]['state'] = STATE_BUY
                    print(code, 'BUY at', code_dict[code]['buy_price'], 'time', tm['time'])
                else:
                    break
        elif code_dict[code]['state'] == STATE_BUY:
            debug_print(code, min_data['time'], 'STATE BUY', 'GAP', code_dict[code]['target_gap'], 'close_price', min_data['close_price'], 'VI', code_dict[code]['vi_highest'])
            profit = (min_data['lowest_price'] - code_dict[code]['buy_price']) / code_dict[code]['buy_price'] * 100
            if bottom_margin == 0:
                bottom_margin = profit
            elif bottom_margin > profit:
                bottom_margin = profit

            if min_data['lowest_price'] < code_dict[code]['vi_highest'] - code_dict[code]['target_gap']:
                print('\t', code, 'FAILED', (min_data['lowest_price'] - code_dict[code]['buy_price']) / code_dict[code]['buy_price'] * 100, 'time', min_data['time'])
                return FAIL
            elif min_data['highest_price'] > code_dict[code]['vi_highest'] + code_dict[code]['target_gap']:
                print('\t', code, 'OK', (min_data['highest_price'] - code_dict[code]['buy_price']) / code_dict[code]['buy_price'] * 100, 'bottom_margin', bottom_margin, 'time', min_data['time'])
                return SUCCESS
    if code_dict[code]['state'] == STATE_BUY:
        return HOLDING

    return NONE

def read_kosdaq_vi_excel(reader, market_code):
    # [{'date': xx, 'alarm_data': []}, ...]
    code_name = dict()
    for code in market_code:
        stock_name = stock_api.request_code_to_name(reader, code)
        if len(stock_name) > 0:
            code_name[stock_name[0]] = code
    print(len(code_name))
    alarm_data_by_date = dict()
    vi_df = pd.read_excel(os.environ['MORNING_PATH'] + os.sep + 'sample_data' + os.sep + 'vi_kosdaq_list.xls')
    vi_df = vi_df.rename({'발동일': 'date', '종목명': 'code_name', '유형명': 'type', '발동시각': 'start_time', '해제시각': 'finish_time'}, axis='columns')
    print('start reading excel', len(vi_df))
    for index, row in vi_df.iterrows():
        d = datetime.strptime(row['date'], '%Y-%m-%d')
        vi_type = row['type']
        stock_name = row['code_name']
        start_time_str = (row['start_time']).split(':')
        finish_time_str = row['finish_time'].split(':')
        start_time = int(start_time_str[0]) * 10000 + int(start_time_str[1]) * 100 + int(start_time_str[2])
        finish_time = int(finish_time_str[0]) * 10000 + int(finish_time_str[1]) * 100 + int(finish_time_str[2])

        if stock_name in code_name:
            if d in alarm_data_by_date:
                alarm_data_by_date[d].append({'0': start_time, '1': ord('1'), '2': 201, '3': code_name[stock_name],
                                            '4': 755})
                alarm_data_by_date[d].append({'0': finish_time, '1': ord('1'), '2': 201, '3': code_name[stock_name],
                                            '4': 756})
            else:
                alarm_data_by_date[d] = [{'0': start_time, '1': ord('1'), '2': 201, '3': code_name[stock_name],
                                            '4': 755}]
                alarm_data_by_date[d].append({'0': finish_time, '1': ord('1'), '2': 201, '3': code_name[stock_name],
                                            '4': 756})
    alarm_list_data = []
    for k, v in alarm_data_by_date.items():
        alarm_list_data.append({'date': k, 'alarm_list': v})
    alarm_list_data = sorted(alarm_list_data, key=lambda x: x['date'])
    print('reading excel done', len(alarm_list_data))
    return alarm_list_data


def iterate_alarm_data(alarm_data, code_dict, target_date):
    done_codes = []
    success_count = 0
    fail_count = 0
    holding_count = 0
    all_count = 0
    for adata in alarm_data:
        #print(adata)
        code = adata['3']
        if code not in market_code:
            continue
        alarm_type = adata['1']
        market_type = adata['2']
        vi_type = adata['4']
        if alarm_type == ord('1') and market_type == 201 and vi_type == 755:
            if code_dict[code]['yesterday_data'] is None: #prevent 2nd
                #print('get past data', code, adata['0'])
                get_past_datas(code, target_date.date(), adata['0'], code_dict) 
        elif alarm_type == ord('1') and market_type == 201 and vi_type == 756:
            if code_dict[code]['yesterday_data'] is not None and code not in done_codes:
                print('-' * 100)
                print('start trade', target_date, code, adata['0'])
                result = start_trade(code, adata['0'], code_dict)
                all_count += 1
                if result == SUCCESS:
                    success_count += 1
                elif result == FAIL:
                    fail_count += 1
                elif result == HOLDING:
                    holding_count += 1
                done_codes.append(code)
    return success_count, fail_count, holding_count, all_count

def start_by_excel(market_code):
    alarm_datas = read_kosdaq_vi_excel(morning_client.get_reader(), market_code)
    success = 0
    fail = 0
    holding = 0
    all_count = 0
    for adata in alarm_datas:
        code_dict = dict()
        for code in market_code:
            code_dict[code] = {'state': STATE_NONE, 'yesterday_data': None, 'today_min_data': None, 'today_min_after_vi': None, 'vi_highest': 0, 'bottom_price': 0, 'buy_price': 0, 'target_gap': 0}

        target_date = adata['date']
        alarm_data = adata['alarm_list']
        s, f, h, a = iterate_alarm_data(alarm_data, code_dict, target_date)
        success += s
        fail += f
        holding += h
        all_count += a
    print('SUCCESS', success, 'FAIL', fail, 'HOLDIONG', holding, 'ALL', all_count)


def start_by_sample(market_code):
    target_date = datetime(2020, 2, 14)
    code_dict = dict()
    for code in market_code:
        code_dict[code] = {'state': STATE_NONE, 'yesterday_data': None, 'today_min_data': None, 'today_min_after_vi': None, 'vi_highest': 0, 'bottom_price': 0, 'buy_price': 0, 'target_gap': 0}

    alarm_data = [#{'0': time, '1': ord('1'), '2': 201, '3': code, '4': 755}, 2020/2/14 test data
                {'0':100635 , '1': ord('1'), '2': 201, '3': 'A064820', '4': 755},
                {'0':100853 , '1': ord('1'), '2': 201, '3': 'A064820', '4': 756}, # OK
                {'0':95825 , '1': ord('1'), '2': 201, '3': 'A016600', '4': 755},
                {'0':100050 , '1': ord('1'), '2': 201, '3': 'A016600', '4': 756},
                {'0':90009, '1': ord('1'), '2': 201, '3': 'A263920', '4': 755},
                {'0':90212, '1': ord('1'), '2': 201, '3': 'A263920', '4': 756},
                {'0':90028, '1': ord('1'), '2': 201, '3': 'A234100', '4': 755},
                {'0':90235, '1': ord('1'), '2': 201, '3': 'A234100', '4': 756},
                {'0':90155, '1': ord('1'), '2': 201, '3': 'A016600', '4': 755},
                {'0':90416, '1': ord('1'), '2': 201, '3': 'A016600', '4': 756},
            ]
    s, f, h, a = iterate_alarm_data(alarm_data, code_dict, target_date)
    print('SUCCESS', s, 'FAIL', f, 'HOLDIONG', h, 'ALL', a)


def start_by_date(market_code, today):
    print('START', today)
    target_date = today
    code_dict = dict()

    for code in market_code:
        code_dict[code] = {'state': STATE_NONE, 'yesterday_data': None, 'today_min_data': None, 'today_min_after_vi': None, 'vi_highest': 0, 'bottom_price': 0, 'buy_price': 0, 'target_gap': 0}
    db_collection = MongoClient(db.HOME_MONGO_ADDRESS).trade_alarm
    alarm_data = list(db_collection['alarm'].find({'date': {'$gte': target_date, '$lte': target_date + timedelta(days=1)}}))
    alarm_data = sorted(alarm_data, key=lambda x: x['date'])
    #alarm_data = list(filter(lambda x: x['3'] == 'A017890', alarm_data))
    s, f, h, a = iterate_alarm_data(alarm_data, code_dict, target_date)
    print('SUCCESS', s, 'FAIL', f, 'HOLDIONG', h, 'ALL', a)


if __name__ == '__main__':
    market_code = morning_client.get_market_code()
    #start_by_date(market_code, datetime(2020, 2, 21))
    start_by_excel(market_code)
    #start_by_sample(market_code)
