import pytest

from configs import client_info
client_info.TEST_MODE = True

import gevent
from clients.scalping_by_amount import tradestatus
from clients.scalping_by_amount.trader import Trader
from clients.scalping_by_amount.buystage import BuyStage
from clients.scalping_by_amount.marketstatus import MarketStatus
from clients.scalping_by_amount.mock import stock_api
from clients.scalping_by_amount import price_info
stock_api.balance = 10000000


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

@pytest.fixture()
def gap_bidask():
    return {
        'fifth_ask_price': 6090, 'fifth_ask_remain': 100,
        'fourth_ask_price': 6080, 'fourth_ask_remain': 100,
        'third_ask_price': 6070, 'third_ask_remain': 100,
        'second_ask_price': 6060, 'second_ask_remain': 100,
        'first_ask_price': 6050, 'first_ask_remain': 100,
        'first_bid_price': 6000, 'first_bid_remain': 100,
        'second_bid_price': 5990, 'second_bid_remain': 100,
        'third_bid_price': 5980, 'third_bid_remain': 100,
        'fourth_bid_price': 5970, 'fourth_bid_remain': 100,
        'fifth_bid_price': 5960, 'fifth_bid_remain': 100}



def test_init():
    code_info = {'is_kospi': False}
    market_status = MarketStatus()
    market_status.status = MarketStatus.IN_MARKET
    bs = BuyStage(None, code_info, market_status, 10000)
    
    assert bs.balance == 10000


def test_buy_with_first_ask(default_bidask):
    market_status = MarketStatus()
    market_status.status = MarketStatus.IN_MARKET
    code_info = {'is_kospi': False}
    bs = BuyStage(None, code_info, market_status, 100000)
    bs.ba_data_handler('A005930', default_bidask)
    assert bs.get_status() == tradestatus.BUY_ORDER_SEND_DONE


def test_buy_with_success_result(default_bidask):
    market_status = MarketStatus()
    market_status.status = MarketStatus.IN_MARKET
    code_info = {'is_kospi': False}
    bs = BuyStage(None, code_info, market_status, 100000) 
    bs.ba_data_handler('A005930', default_bidask)
    bs.receive_result({'flag': '4', 'order_number': 12345, 'price': 6050, 'quantity': 16})
    assert bs.get_status() == tradestatus.BUY_ORDER_CONFIRM
    bs.receive_result({'flag': '1', 'order_number': 12345, 'price': 6050, 'quantity': 16})
    assert bs.get_status() == tradestatus.BUY_DONE

def test_buy_with_some(default_bidask):
    market_status = MarketStatus()
    market_status.status = MarketStatus.IN_MARKET
    code_info = {'is_kospi': False}
    bs = BuyStage(None, code_info, market_status, 100000)
    bs.ba_data_handler('A005930', default_bidask)
    bs.receive_result({'flag': '4', 'order_number': 12345, 'price': 6050, 'quantity': 16})
    assert bs.get_status() == tradestatus.BUY_ORDER_CONFIRM
    bs.receive_result({'flag': '1', 'order_number': 12345, 'price': 6050, 'quantity': 15})
    assert bs.get_status() == tradestatus.BUY_SOME
    bs.receive_result({'flag': '1', 'order_number': 12345, 'price': 6050, 'quantity': 1})
    assert bs.get_status() == tradestatus.BUY_DONE


def test_buy_with_gap_bidask(gap_bidask):
    market_status = MarketStatus()
    market_status.status = MarketStatus.IN_MARKET
    code_info = {'is_kospi': False}
    bs = BuyStage(None, code_info, market_status, 100000)
    bs.ba_data_handler('A005930', gap_bidask)
    assert bs.get_status() == tradestatus.BUY_FAIL

