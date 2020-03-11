import pytest

from configs import client_info
client_info.TEST_MODE = True

from clients.scalping_by_amount import tradestatus
from clients.scalping_by_amount.sellstage import SellStage
from clients.scalping_by_amount.marketstatus import MarketStatus
from clients.scalping_by_amount.mock import stock_api
from clients.scalping_by_amount import price_info
from clients.common import morning_client
from morning_server import message
import gevent


@pytest.fixture()
def default_bidask():
    return {
        'fifth_ask_price': 6090, 'fifth_ask_remain': 100,
        'fourth_ask_price': 6080, 'fourth_ask_remain': 100,
        'third_ask_price': 6070, 'third_ask_remain': 100,
        'second_ask_price': 6060, 'second_ask_remain': 100,
        'first_ask_price': 6050, 'first_ask_remain': 100,
        'first_bid_price': 6040, 'first_bid_remain': 100,
        'second_bid_price': 6030, 'second_bid_remain': 100,
        'third_bid_price': 6020, 'third_bid_remain': 100,
        'fourth_bid_price': 6010, 'fourth_bid_remain': 100,
        'fifth_bid_price': 6000, 'fifth_bid_remain': 100}


def down_bidask(bidask_table):
    keys = ['first_ask_price', 'second_ask_price', 'third_ask_price', 'fourth_ask_price', 'fifth_ask_price',
            'first_bid_price', 'second_bid_price', 'third_bid_price', 'fourth_bid_price', 'fifth_bid_price']
    for k in keys:
        price = bidask_table[k]
        unit = morning_client.get_ask_bid_price_unit(message.KOSDAQ, price-1)
        bidask_table[k] = price - unit


def test_init():
    ss = SellStage(None, None, None, 1000, 10, False)
    assert ss.get_status() == tradestatus.SELL_WAIT


def test_send_first_ba(default_bidask):
    bidask = default_bidask.copy()
    market_status = MarketStatus()
    market_status.status = MarketStatus.IN_MARKET
    code_info = {'yesterday_close': 6000, # 10 ba unit
                'today_open': 6030,
                'is_kospi': False}

    ss = SellStage(None, code_info, market_status, 6050, 10, False)
    ss.ba_data_handler('A005930', bidask)
    assert ss.get_status() == tradestatus.SELL_PROGRESSING


def test_cut_off(default_bidask):
    bidask = default_bidask.copy()
    market_status = MarketStatus()
    market_status.status = MarketStatus.IN_MARKET
    current_order_num = stock_api.current_order_number
    code_info = {'yesterday_close': 6000, # 10 ba unit
                'today_open': 6030,
                'is_kospi': False}

    ss = SellStage(None, code_info, market_status, 6050, 10, False)
    ss.ba_data_handler('A005930', bidask)
    assert ss.get_status() == tradestatus.SELL_PROGRESSING
    ss.receive_result({'flag': '4',
                        'order_number': current_order_num,
                        'price': 6070,
                        'quantity': 3})

    ss.receive_result({'flag': '4',
                        'order_number': current_order_num + 1,
                        'price': 6080,
                        'quantity': 3})

    ss.receive_result({'flag': '4',
                        'order_number': current_order_num + 2,
                        'price': 6090,
                        'quantity': 4})
    gevent.sleep(2)
    down_bidask(bidask)
    ss.ba_data_handler('A005930', bidask)
    down_bidask(bidask)
    ss.ba_data_handler('A005930', bidask)

    assert len(ss.order_queue.get_ready_order_list()) == 2


def test_sell_done(default_bidask):
    bidask = default_bidask.copy()
    market_status = MarketStatus()
    market_status.status = MarketStatus.IN_MARKET
    current_order_num = stock_api.current_order_number
    code_info = {'yesterday_close': 6000, # 10 ba unit
                'today_open': 6030,
                'is_kospi': False,
                'code': 'A005930'}

    ss = SellStage(None, code_info, market_status, 6050, 10, False)
    ss.ba_data_handler('A005930', bidask)
    assert ss.get_status() == tradestatus.SELL_PROGRESSING
    ss.receive_result({'flag': '4',
                        'order_number': current_order_num,
                        'price': 6070,
                        'quantity': 3})

    ss.receive_result({'flag': '4',
                        'order_number': current_order_num + 1,
                        'price': 6080,
                        'quantity': 3})

    ss.receive_result({'flag': '4',
                        'order_number': current_order_num + 2,
                        'price': 6090,
                        'quantity': 4})
    gevent.sleep(2)
    ss.receive_result({'flag': '1',
                        'order_number': current_order_num,
                        'price': 6070,
                        'quantity': 3})
    ss.receive_result({'flag': '1',
                        'order_number': current_order_num + 1,
                        'price': 6080,
                        'quantity': 3})

    ss.receive_result({'flag': '1',
                        'order_number': current_order_num + 2,
                        'price': 6090,
                        'quantity': 4})
    assert ss.get_status() == tradestatus.SELL_DONE
