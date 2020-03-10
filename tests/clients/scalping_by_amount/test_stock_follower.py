import pytest

from configs import client_info
client_info.TEST_MODE = True

from clients.scalping_by_amount import tradestatus
from clients.scalping_by_amount.stock_follower import StockFollower
from clients.scalping_by_amount.marketstatus import MarketStatus
from clients.common import morning_client
from morning.back_data import holidays
from morning_server import stock_api
from clients.scalping_by_amount import mock_stock_api as mstock_api
from morning.pipeline.converter import dt
from configs import db

from pymongo import MongoClient
from datetime import datetime, timedelta

def get_tick_data(code, from_datetime, until_datetime, db_collection, is_ba):
    data = list(db_collection[code].find({'date': {'$gte': from_datetime, '$lte': until_datetime}}))
    converted_data = []
    for td in data:
        if is_ba:
            converted = dt.cybos_stock_ba_tick_convert(td)
        else:
            converted = dt.cybos_stock_tick_convert(td)
        converted_data.append(converted)
    return converted_data


@pytest.fixture()
def tick_data():
    code = 'A290720'
    from_datetime = datetime(2020, 2, 27, 8, 0, 0)
    until_datetime = datetime(2020, 2, 27, 10, 0, 0)
    trade_start_time = datetime(2020, 2, 27, 9, 0, 3)
    yesterday = holidays.get_yesterday(from_datetime.date())
    yesterday_data = morning_client.get_past_day_data(code, yesterday, yesterday)[0]
    yesterday_data['code'] = code
    
    print('call fixture')
    db_collection = MongoClient(db.HOME_MONGO_ADDRESS).trade_alarm
    all_tick = []
    tick = get_tick_data(code, from_datetime, until_datetime, db_collection, False)
    all_tick.extend(tick)
    ba_tick = get_tick_data(code +'_BA', trade_start_time, until_datetime, db_collection, True)
    all_tick.extend(ba_tick)
    all_tick = sorted(all_tick, key=lambda x: x['date'])
    return code, all_tick, yesterday_data


def test_create(tick_data):
    code, tick, yesterday_data = tick_data
    start_trading_time = datetime(2020, 2, 27, 9, 0, 3)
    started = False
    sf = StockFollower(None, code, , False)
    start_time = tick[0]['date']
    for t in tick:
        if 'first_bid_price' in t:
            sf.ba_data_handler(code, [t])
        else:
            sf.tick_data_handler(code, [t])

        if t['date'] - start_time > timedelta(seconds=1):
            sf.process_tick()
            start_time = t['date']

        if not started and start_time >= start_trading_time:
            code_info = {'code': code, 'is_kospi': False}
            sf.start_trading(code_info)
            started = True

        if len(mstock_api.order_list) > 0 and mstock_api.order_list[0]['is_buy']:
            sf.receive_result({'flag': '4', 'order_number':12345, 
                'quantity': mstock_api.order_list[0]['quantity']})
            sf.receive_result({'flag': '1', 'order_number':12345, 'price': 22000,
                'quantity': mstock_api.order_list[0]['quantity']})
            mstock_api.clear_all()
    assert 1 == 0

