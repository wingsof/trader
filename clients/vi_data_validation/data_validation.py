from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))


from clients.common import morning_client
from datetime import datetime, date, time, timedelta
from morning.back_data import holidays
from morning_server import stock_api
from morning_server import message
import gevent
from gevent.queue import Queue
from configs import db
from pymongo import MongoClient
from utils import time_converter
from utils import slack


db_collection = None
SEND_SLACK = True


def send_slack_message(msg):
    if SEND_SLACK:
        slack.send_slack_message(msg)


def validate_tick_data(code, today, h=0, m=0):
    from_datetime = datetime.combine(today, time(h,m))
    until_datetime = datetime.combine(today + timedelta(days=1), time(0,0))
    data = list(db_collection[code].find({'date': {'$gte': from_datetime, '$lte': until_datetime}}))
    # from 9 am to 3:20 pm no gap over 5 minutes
    if len(data) < 100: # at least 100 (because consider alarm datetime)
        print(code, 'length is not enough')
        return False

    start_time = data[0]['date']
    end_time = data[-1]['date']
    current_time = start_time
    if h == 0 and m == 0 and start_time.hour > 9:
        print(code, 'first data is over 9 am')
        return False

    if end_time.hour < 15:
        print(code, 'data at the end is under 3 pm', end_time)
        return False

    for d in data:
        if d['date'] - current_time > timedelta(minutes=5):
            if d['date'].hour <= 15 and d['date'].minute <= 20:
                print(code, 'time gap is bigger than 5 min', d['date'] - current_time, d['date'], current_time)
                return False
        current_time = d['date']

    return True


def validate_ba_tick_data(code, today, h=0, m=0):
    return validate_tick_data(code + message.BIDASK_SUFFIX, today, h, m)


def get_alarm_list(today):
    target_date = datetime.combine(today, time(0,0))
    alarm_data = list(db_collection['alarm'].find({'date': {'$gte': target_date, '$lte': target_date + timedelta(days=1)}}))
    alarm_data = sorted(alarm_data, key=lambda x: x['date'])
    alarm_list = []
    alarm_code_list = []
    for ad in alarm_data:
        if ad['3'] not in alarm_code_list and ad['1'] == ord('1') and ad['2'] == 201 and ad['4'] == 755:# or ad['4'] == 756):
            alarm_list.append(ad)
            alarm_code_list.append(ad['3'])
    return alarm_list


def validate_alarm_data(code, today, alarm_datetime):
    if not validate_tick_data(code, today, alarm_datetime.hour, alarm_datetime.minute):
        print('Failed alarm tick data')
        return False
    elif not validate_ba_tick_data(code, today, alarm_datetime.hour, alarm_datetime.minute):
        print('Failed alarm ba tick data')
        return False
    return True


def start_validation(codes=[]):
    global db_collection
    send_slack_message('START VALIDATION')

    if len(codes) > 0:
        market_code = codes
    else:
        market_code = morning_client.get_market_code()

    today = datetime.now().date()
    yesterday = holidays.get_yesterday(today)
    db_collection = MongoClient(db.HOME_MONGO_ADDRESS).trade_alarm

    yesterday_list = []
    for progress, code in enumerate(market_code):
        print('collect yesterday data', f'{progress+1}/{len(market_code)}', end='\r')
        data = morning_client.get_past_day_data(code, yesterday, yesterday)
        if len(data) == 1:
            data = data[0]
            data['code'] = code
            #yesterday_data[code] = data
            yesterday_list.append(data)
    print('')
    yesterday_list = sorted(yesterday_list, key=lambda x: x['amount'], reverse=True)
    yesterday_list = yesterday_list[:100]
    failed_tick_codes = []
    failed_ba_tick_codes = []
    # 1. validate yesterday_list :100's today tick data
    for ydata in yesterday_list:
        if not validate_tick_data(ydata['code'], today):
            failed_tick_codes.append(ydata['code'])
        if not validate_ba_tick_data(ydata['code'], today):
            failed_ba_tick_codes.append(ydata['code'])

    if len(failed_tick_codes) > 0:
        send_slack_message('FAILED TICK ' + str(failed_tick_codes))
        print('FAILED TICK', failed_tick_codes)
    else:
        send_slack_message('TICK ALL SUCCESS')
        print('TICK ALL SUCCESS')

    if len(failed_ba_tick_codes) > 0:
        send_slack_message('FAILED BA TICK ' + str(failed_ba_tick_codes))
        print('FAILED BA TICK', failed_ba_tick_codes)
    else:
        send_slack_message('TICK BA ALL SUCCESS')
        print('TICK BA ALL SUCCESS')

    # 2. validate today alarm tick data 
    alarm_list = get_alarm_list(today)
    alarm_failed_codes = []
    if len(alarm_list) > 0:
        for ac in alarm_list:
            if len(codes) > 0 and ac['3'] not in codes:
                continue

            if not validate_alarm_data(ac['3'], today, ac['date']):
                alarm_failed_codes.append(ac['3'])

        if len(alarm_failed_codes) > 0:
            send_slack_message('FAILED ALARM CODES ' + str(alarm_failed_codes) + '\t' + str(len(alarm_failed_codes)) + ' / ' + str(len(alarm_list)))
            print('FAILED ALARM CODES', alarm_failed_codes, len(alarm_failed_codes), '/', len(alarm_list))
        else:
            send_slack_message('ALARM ALL SUCCESS ' + str(len(alarm_list)))
            print('ALARM ALL SUCCESS', len(alarm_list))
    else:
        send_slack_message('NO ALARM TODAY')
        print('NO ALARM TODAY')
    sys.exit(0)

if __name__ == '__main__':
    SEND_SLACK = False
    if len(sys.argv) > 1:
        start_validation(sys.argv[1:])
    else:
        start_validation()
