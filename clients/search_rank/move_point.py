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


highest_in_year = {}
highest_in_today = {}
yesterday_close = {}
yesterday_amount = {}
today_open_price = {}

STATE_START = 0
STATE_UNDER_MAVG = 1
STATE_MEET_MAVG = 2



def get_yesterday_day_data(query_date, market_code):
    yesterday_list = []
    for progress, code in enumerate(market_code):
        print('collect data', f'{progress+1}/{len(market_code)}', end='\r')
        data = morning_client.get_past_day_data(code, query_date, query_date)
        if len(data) == 1:
            data = data[0]
            data['code'] = code
            yesterday_list.append(data)
    print('')
    return yesterday_list


def is_price_in_range(query_date, code):
    data = morning_client.get_past_day_data(code, query_date - timedelta(days=365), query_date)
    if len(data) > 2:
        highest_price = max([d['highest_price'] for d in data])
        highest_in_year[code] = highest_price
        current_price = data[-1]['close_price']
        profit_from_highest = (current_price - highest_price) / highest_price * 100.0
        if -20.0 <= profit_from_highest:
            return True
    return False


def get_profit(a, b):
    p = (a - b) / b * 100.0
    p = float("{0:.2f}".format(p))
    return p


def start_trading(tdate, codes):
    print('Start', tdate, len(codes)) 
    yesterday = holidays.get_yesterday(tdate)
    start_time = datetime.now()

    yesterday_data = get_yesterday_day_data(yesterday, codes)

    amount_passed = []
    for data in yesterday_data:
        code = data['code']
        if data['amount'] >= 3000000000:
            yesterday_close[code] = data['close_price']
            yesterday_amount[code] = data['amount']
            amount_passed.append(code)
    print('amount passed', len(amount_passed))
    range_passed = []
    for code in amount_passed:
        if is_price_in_range(yesterday, code):
            range_passed.append(code)
    print('range passed', len(range_passed))

    meet_codes = []
    for code in range_passed:
        state = STATE_START
        highest_in_today[code] = 0
        tdata = morning_client.get_minute_data(code, tdate, tdate)
        ydata = morning_client.get_minute_data(code, yesterday, yesterday)

        if len(tdata) == 0:
            print(code, 'Today Min DATA is empty')
            continue

        current_data = []
        current_data.extend(ydata)
        today_open_price[code] = tdata[0]['start_price']
        today_amount = 0

        for data in tdata:
            current_data.append(data)

            if data['time'] <= 930:
                today_amount += data['amount']
                if data['highest_price'] > highest_in_today[code]:
                    highest_in_today[code] = data['highest_price']
                continue
            else:
                if yesterday_amount[code] > today_amount:
                    continue

                mavg = statistics.mean([d['close_price'] for d in current_data[-60:]])

                if state == STATE_START:
                    if mavg < data['highest_price']:
                        if data['highest_price'] > highest_in_today[code]:
                            highest_in_today[code] = data['highest_price']
                    else:
                        state = STATE_UNDER_MAVG

                if state == STATE_UNDER_MAVG:
                    if data['close_price'] >= mavg * 1.01:
                        state = STATE_MEET_MAVG

                if state == STATE_MEET_MAVG:
                    meet_codes.append({'code': code,
                                       'date': data['0'],
                                       'time':  data['time'],
                                       'open profit': get_profit(today_open_price[code], yesterday_close[code]),
                                       'current profit:': get_profit(data['close_price'], yesterday_close[code]),
                                       'mavg': mavg,
                                       'current_close': data['close_price'],
                                       'current_highest': data['highest_price']})
                    print(meet_codes)
                    break
                    # calculate target price
                    # or cut when meet under mavg / 0 % cut
    return meet_codes


if __name__ == '__main__':
    target_date = datetime.strptime(sys.argv[1], '%Y-%m-%d').date()
    kosdaq_market_code = morning_client.get_market_code()
    #kosdaq_market_code = ['A001540']
    result = start_trading(target_date, kosdaq_market_code)
    
    df = pd.DataFrame(result)
    df.to_excel('mpoint' + sys.argv[1] + '.xlsx')
