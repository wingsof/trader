from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))
from configs import client_info
client_info.TEST_MODE = True


from clients.scalping_by_amount.mock import stock_api
from clients.scalping_by_amount.mock import datetime
from clients.common import morning_client
from datetime import datetime as rdatetime
from clients.scalping_by_amount import main
from configs import db
from pymongo import MongoClient

datetime.current_datetime = rdatetime(2020, 3, 11, 8, 55)
finish_time = rdatetime(2020, 3, 11, 15, 35)
market_codes = morning_client.get_all_market_code()


def start_provide_tick():
    db_collection = MongoClient(db.HOME_MONGO_ADDRESS).trade_alarm
    while datetime.current_datetime <= finish_time:
        from_time = datetime.current_datetime
        until_time = from_time + timedelta(minutes=1)
        # read DB and sort it and distribute it to subscriber
        period_ticks = []
        for code in market_codes:
            tick_data = list(db_collection[code].find({'date': {'$gte': from_time, '$lte': until_time}}))
            for t in tick_data:
                t['code'] = code
            ba_tick_data = list(db_collection[code+'_BA'].find({'date': {'$gte': from_time, '$lte': until_time}}))
            for bt in ba_tick_data:
                bt['code'] = code
            period_ticks.extend(tick_data)
            period_ticks.extend(ba_tick_data)

        period_ticks = sorted(period_ticks, key=lambda x: x['date'])
        for tick in period_ticks:
            if 'first_bid_price' in tick:
                stock_api.send_bidask_data(tick['code'], tick)
            else:
                stock_api.send_tick_data(tick['code'], tick)
            datetime.current_datetime = tick['date']

        if from_time == datetime.current_datetime:
            datetime.current_datetime = until_time


tick_thread = gevent.spawn(start_provide_tick)
main.start_trader()

gevent.joinall([tick_thread])
