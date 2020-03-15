from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))


from utils import trade_logger as logger
from clients.common import morning_client
from datetime import timedelta
from morning.back_data import holidays
from configs import client_info
if client_info.TEST_MODE:
    from clients.scalping_by_amount.mock import stock_api
    from clients.scalping_by_amount.mock import datetime
else:
    from morning_server import stock_api
    from datetime import datetime

from morning_server import message
import gevent
from gevent.queue import Queue
from clients.scalping_by_amount import stock_follower
from clients.scalping_by_amount import pickstock
from clients.scalping_by_amount import time
from configs import db
from pymongo import MongoClient
from utils import time_converter
from configs import time_info


followers = []
DELTA = 0
MINIMUM_AMOUNT = 100000000
candidate_queue = gevent.queue.Queue()

def vi_handler(_, data):
    data = data[0]


def data_process():
    picker = pickstock.PickStock()
    now = datetime.now()
    start_time = now.replace(hour=9+DELTA, minute=0, second=3)
    done_time = now.replace(hour=15+DELTA, minute=10, second=0)
    pick_finish_time = now.replace(hour=15+DELTA, minute=5, second=0)
    entered = False

    while True:
        if start_time <= datetime.now() <= done_time:
            entered = True
            time.sleep(10)

            candidates = []
            for sf in followers:
                snapshot = sf.snapshot(10)
                if (snapshot is None or
                    not sf.is_in_market() or
                    snapshot['profit'] < 0.5 or
                    snapshot['yesterday_close'] == 0 or
                    snapshot['today_open'] == 0 or
                    snapshot['today_open'] < snapshot['yesterday_close'] or
                    snapshot['amount'] < MINIMUM_AMOUNT):
                    continue
                candidates.append(snapshot)
            picked = picker.pick_one(candidates)
            if picked is not None and datetime.now() <= pick_finish_time:
                logger.info('PICKED %s, amount: %d, profit: %f', picked['code'], picked['amount'],
                            picked['profit'])
                candidate_queue.put_nowait({'code': picked['code'], 'info': picked})
        else:
            if entered:
                logger.info('QUEUE EXIT')
                candidate_queue.put_nowait({'code': 'exit', 'info': None})
                entered = False
                break
        time.sleep(0.3)


def receive_result(result):
    logger.warning('TRADE RESULT\n%s', str(result))
    for fw in followers:
        fw.receive_result(result)


def heart_beat():
    last_processed_time = datetime.now()
    trading_follower = None
    finish_flag = False
    while True:
        while datetime.now() - last_processed_time < timedelta(seconds=1):
            time.sleep(0.05)

        picked_code = None
        candidates = []
        while not candidate_queue.empty():
            candidates.append(candidate_queue.get())

        for c in candidates:
            if c['code'] == 'exit':
                logger.warning('SET FINISH FLAG')
                finish_flag = True

        if finish_flag:
            if trading_follower is None:
                logger.warning('FINISH TODAY WORK')
                break
            else:
                logger.warning('SEND FINISH WORK')
                trading_follower.finish_work()
        else:
            if trading_follower is None:
                if len(candidates) > 0:
                    picked_code = candidates[-1]
                    candidates.clear()

            if picked_code is not None and picked_code['code'] == 'exit':
                finish_flag = True

            for fw in followers:
                fw.process_tick()
                if picked_code is not None and fw.code == picked_code['code']:
                    if fw.is_in_market():
                        trading_follower = fw
                        fw.start_trading(picked_code['info'])

        if trading_follower is not None:
            if trading_follower.is_trading_done():
                trading_follower = None

        last_processed_time = datetime.now()

def get_yesterday_data(today, market_code):
    yesterday = holidays.get_yesterday(today)
    yesterday_list = []
    for progress, code in enumerate(market_code):
        print('collect yesterday data', f'{progress+1}/{len(market_code)}', end='\r')
        data = morning_client.get_past_day_data(code, yesterday, yesterday)
        if len(data) == 1:
            data = data[0]
            data['code'] = code
            yesterday_list.append(data)
    print('')
    return yesterday_list


def start_trader(ready_queue=None):
    print('start trader', datetime.now())
    market_code = []
    kosdaq_code = morning_client.get_market_code()
    kospi_code = morning_client.get_market_code(message.KOSPI)
    market_code.extend(kosdaq_code)
    market_code.extend(kospi_code)

    market_code = list(dict.fromkeys(market_code))
    market_code =  list(filter(lambda x: len(x) > 0 and x[1:].isdigit(), market_code))
    yesterday_list = get_yesterday_data(datetime.now(), market_code) 
    yesterday_list = sorted(yesterday_list, key=lambda x: x['amount'], reverse=True)
    yesterday_list = yesterday_list[:1000]

    for yesterday_data in yesterday_list:
        code = yesterday_data['code']
        sf = stock_follower.StockFollower(morning_client.get_reader(), code, yesterday_data, code in kospi_code)
        sf.subscribe_at_startup()
        followers.append(sf)

    stock_api.subscribe_alarm(morning_client.get_reader(), vi_handler)
    stock_api.subscribe_trade(morning_client.get_reader(), receive_result)

    if ready_queue is not None:
        ready_queue.put_nowait([yl['code'] for yl in yesterday_list])
    gevent.joinall([gevent.spawn(heart_beat), gevent.spawn(data_process)])


if __name__ == '__main__':
    start_trader()
