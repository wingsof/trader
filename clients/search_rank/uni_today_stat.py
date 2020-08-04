from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))

import gevent
from clients.common import morning_client
from datetime import datetime, date, timedelta, time
import statistics
from morning.back_data import holidays
from morning_server import stock_api, message
from gevent.queue import Queue
from configs import db
from morning.pipeline.converter import dt
import pandas as pd



def get_yesterday_day_data(query_date, market_code):
    yesterday_dict = {}
    for progress, code in enumerate(market_code):
        print('collect data', f'{progress+1}/{len(market_code)}', end='\r')
        data = morning_client.get_past_day_data(code, query_date, query_date)
        if len(data) == 1:
            data = data[0]
            data['code'] = code
            yesterday_dict[code] = data
    print('')
    return yesterday_dict


def get_yesterday_uni_day_data(query_date, market_code):
    yesterday_uni_list = []
    for progress, code in enumerate(market_code):
        print('collect uni data', f'{progress+1}/{len(market_code)}', end='\r')
        data = morning_client.get_uni_day_period_data(code, query_date - timedelta(days=7), query_date)
        if len(data) >= 3:
            prev_data = data[:-1]
            data = data[-1]

            if data['start_price'] == 0:
                continue
            prev_max_amount = max([d['volume'] * d['close_price'] for d in prev_data])
            data['code'] = code
            data['amount'] = data['volume'] * data['close_price']
            data['market_close'] = data['close_price'] - data['market_close_diff']
            if data['amount'] >= 1000000000 and data['amount'] > prev_max_amount:
                yesterday_uni_list.append(data)
    print('')
    return yesterday_uni_list


def get_profit(a, b):
    p = (a - b) / b * 100.0
    p = float("{0:.2f}".format(p))
    return p


def start_trading(tdate, codes):
    print('Start', tdate, len(codes)) 
    yesterday = holidays.get_yesterday(tdate)
    start_time = datetime.now()
    yesterday_uni_data = get_yesterday_uni_day_data(yesterday, codes)
    print('Uni data count', len(yesterday_uni_data))
    yesterday_uni_data = sorted(yesterday_uni_data, key=lambda x: x['market_close_profit'], reverse=True)
    codes = [d['code'] for d in yesterday_uni_data]
    yesterday_dict = get_yesterday_day_data(yesterday, codes)
    result = []
    for ud in yesterday_uni_data:
        tdata = morning_client.get_minute_data(ud['code'], tdate, tdate)
        highest = 0
        amount = 0
        highest_time = None
        open_price = 0
        for d in tdata:
            if open_price == 0:
                open_price = d['start_price']

            if d['time'] > 931:
                break
            if d['highest_price'] > highest:
                highest = d['highest_price']
                highest_time = d['time']
            amount += d['amount']

        if highest_time is not None:
            if ud['market_close'] == 0:
                print('close 0', ud)
                continue

            ud['date'] = d['0']
            ud['today_open_price'] = open_price
            ud['today_open_profit'] = get_profit(open_price, ud['market_close'])
            ud['today_highest_time'] = highest_time
            ud['today_highest_price'] = highest
            ud['today_max_profit'] = get_profit(highest, ud['market_close'])
            ud['today_amount'] = amount
            ud['yesterday_amount'] = yesterday_dict[ud['code']]['amount']
            result.append(ud)

    return result


if __name__ == '__main__':
    target_date = datetime.strptime(sys.argv[1], '%Y-%m-%d').date()
    market_codes = morning_client.get_all_market_code()
    #kosdaq_market_code = ['A001540']
    result = start_trading(target_date, market_codes)
    
    df = pd.DataFrame(result)
    df.to_excel('ud_' + sys.argv[1] + '.xlsx')
