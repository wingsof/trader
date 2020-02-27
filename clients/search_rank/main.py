from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))


from clients.common import morning_client
from datetime import datetime, date, timedelta, time
from morning.back_data import holidays
from morning_server import stock_api, message
import gevent
from gevent.queue import Queue
from configs import db
from pymongo import MongoClient
from morning.pipeline.converter import dt
import numpy as np
from scipy.signal import find_peaks, peak_prominences
import pandas as pd


def start_search(code, search_time, kosdaq_market_code):
    search_time = datetime.strptime(search_time, '%Y-%m-%d %H:%M')

    # Since kiwoom start minute from 900 but creon starts from 901
    search_time_hr = search_time.hour * 100 + search_time.minute + 1
    data_list = []
    for kosdaq_code in kosdaq_market_code:
        data = morning_client.get_minute_data(kosdaq_code, search_time.date(), search_time.date())
        fdata = list(filter(lambda x: x['time'] == search_time_hr, data)) 
        if len(fdata) == 1:
            stock_data = fdata[0]
            profit = (stock_data['close_price'] - stock_data['start_price']) / stock_data['start_price'] * 100
            data_list.append({'code': kosdaq_code, 'profit': profit, 'amount': stock_data['amount']})
        #else:
        #    print(kosdaq_code, 'len', len(fdata), len(data))
    by_profit = sorted(data_list, key=lambda x: x['profit'], reverse=True)
    print('*' * 100)
    for bp in enumerate(by_profit[:10]):
        print(bp)
    print('*' * 100)

    for i, bp in enumerate(by_profit):
        if bp['code'] == code:
            print('by profit rank', i+1)
            print(bp)
            break

    by_amount = sorted(data_list, key=lambda x: x['amount'], reverse=True)
    print('*' * 100)
    for ba in enumerate(by_amount[:10]):
        print(ba)
    print('*' * 100)

    print('amount rank1', by_amount[0]['amount'])
    for i, ba in enumerate(by_amount):
        if ba['code'] == code:
            print('by amount rank', i+1)
            print(ba)
            break


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(sys.argv[0], 'code', 'time(2020-02-03 09:00)')
        sys.exit(1)

    code = sys.argv[1]
    search_time = sys.argv[2]
    print(search_time)
    kosdaq_market_code = morning_client.get_market_code()
    kospi_market_code = morning_client.get_market_code(message.KOSPI)
    kosdaq_market_code.extend(kospi_market_code)

    print(len(kosdaq_market_code))
    if code in kosdaq_market_code:
        start_search(code, search_time, kosdaq_market_code)
    else:
        print('Cannot find code', code)
