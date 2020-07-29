from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))

import gevent
from clients.common import morning_client
from datetime import datetime, date, timedelta, time
from morning.back_data import holidays
from morning_server import stock_api, message
from gevent.queue import Queue
from configs import db
from morning.pipeline.converter import dt
import pandas as pd


yesterday_data = {}
result = []

def get_day_data(query_date, market_code):
    for progress, code in enumerate(market_code):
        print('collect data', f'{progress+1}/{len(market_code)}', end='\r')
        data = morning_client.get_past_day_data(code, query_date, query_date)
        if len(data) == 1:
            data = data[0]
            data['code'] = code
            yesterday_data[code] = data
    print('')


def start_trading(tdate, codes):
    print('Start', tdate, len(codes)) 
    yesterday = holidays.get_yesterday(tdate)

    get_day_data(yesterday, codes)
    for progress, code in enumerate(codes):
        if code not in yesterday_data or yesterday_data[code]['amount'] == 0:
            continue

        tdata = morning_client.get_minute_data(code, tdate, tdate)
        amount = 0
        start_watch = False
        found_point = None
        post_time = None
        previous_data = None
        start_data = None
        report = {'date': tdate.year * 10000 + tdate.month * 100 + tdate.day, 'code': code, 'amount': 0, 'yesterday_amount': 0, 'buy_point_profit': 0, 'from_open_profit': 0,
                  'pre_highest': 0, 'post_highest': 0, 'over_pre_high_time': 0, 'buy_price': 0, 'post_high_time': 0, 'amount_x': 0,
                  'post_low_time': 0, 'low_price': 0, 'high_profit': 0, 'low_profit': 0}

        for data in tdata:
            if start_data is None:
                start_data = data

            if data['time'] <= 930:
                amount += data['amount']
                if data['highest_price'] > report['pre_highest']:
                    report['pre_highest'] = data['highest_price']
                continue
            elif not start_watch and data['time'] > 930 and amount > yesterday_data[code]['amount'] and data['highest_price'] < report['pre_highest'] and amount > 1000000000:
                start_watch = True
                report['amount'] = amount
                report['yesterday_amount'] = yesterday_data[code]['amount']

            if not start_watch:
                break

            if found_point is None:
                if data['time'] >= 1449:
                    break
                else:
                    if data['close_price'] > data['start_price'] and data['highest_price'] > report['pre_highest']:
                        found_point = datetime(tdate.year, tdate.month, tdate.day, int(data['time'] / 100), int(data['time'] % 100), 0)
                        report['over_pre_high_time'] = data['time']
                        report['buy_price'] = data['highest_price']
                        report['buy_point_profit'] = float("{0:.2f}".format((report['buy_price'] - yesterday_data[code]['close_price']) / yesterday_data[code]['close_price'] * 100.0))
                        report['from_open_profit'] = float("{0:.2f}".format((report['buy_price'] - start_data['start_price']) / start_data['start_price'] * 100.0))
            else:
                dt = datetime(tdate.year, tdate.month, tdate.day, int(data['time'] / 100), int(data['time'] % 100), 0)

                if dt - found_point >= timedelta(minutes=30):
                    report['amount_x'] = float("{0:.2f}".format(amount / yesterday_data[code]['amount']))
                    report['high_profit'] = float("{0:.2f}".format((report['post_highest'] - report['buy_price']) / report['buy_price'] * 100.0))
                    report['low_profit'] = float("{0:.2f}".format((report['low_price'] - report['buy_price']) / report['buy_price'] * 100.0))
                    result.append(report)
                    break
                else:
                    if data['highest_price'] > report['post_highest']:
                        report['post_highest'] = data['highest_price']
                        report['post_high_time'] = data['time']

                    if report['low_price'] == 0 or data['lowest_price'] < report['low_price']:
                        report['low_price'] = data['lowest_price']
                        report['post_low_time'] = data['time']

if __name__ == '__main__':
    target_date = datetime.strptime(sys.argv[1], '%Y-%m-%d').date()
    kosdaq_market_code = morning_client.get_market_code()

    while target_date <= datetime(2020, 6, 15, 0, 0, 0).date():
        if holidays.is_holidays(target_date):
            target_date += timedelta(days=1)
            continue
        start_trading(target_date, kosdaq_market_code)
        target_date += timedelta(days=1)


    df = pd.DataFrame(result)
    df.to_excel('930.xlsx')
