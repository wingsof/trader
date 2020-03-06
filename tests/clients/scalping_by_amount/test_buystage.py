import pytest

from configs import client_info
client_info.TEST_MODE = True

from clients.scalping_by_amount import tradestatus
from clients.scalping_by_amount.buystage import BuyStage
from clients.scalping_by_amount.marketstatus import MarketStatus
from clients.scalping_by_amount import mock_stock_api, price_info


def test_init():
    market_status = MarketStatus()
    market_status.status = MarketStatus.IN_MARKET
    bs = BuyStage(None, market_status, 10000)
    
    assert bs.balance == 10000


def test_buy_with_first_ask():
    market_status = MarketStatus()
    market_status.status = MarketStatus.IN_MARKET
    bs = BuyStage(None, market_status, 10000)

    ba = {'first_ask_price': 6050,
            'second_ask_price': 6060,
            'third_ask_price': 6070,
            'first_ask_remain': 100,
            'second_ask_remain': 100,
            'third_ask_remain': 100}
    bs.ba_data_handler('A005930', ba)
    ordered_list = mock_stock_api.order_list
    assert len(ordered_list) == 1
    assert ordered_list[0]['price'] == 6050
    ordered_list.clear()


def test_buy_with_second_ask():
    market_status = MarketStatus()
    market_status.status = MarketStatus.IN_MARKET
    bs = BuyStage(None, market_status, 18000)
    ba = {'first_ask_price': 6050,
            'second_ask_price': 6060,
            'third_ask_price': 6070,
            'first_ask_remain': 1,
            'second_ask_remain': 1,
            'third_ask_remain': 1}
    bs.ba_data_handler('A005930', ba)
    ordered_list = mock_stock_api.order_list
    assert len(ordered_list) == 1
    assert ordered_list[0]['price'] == 6060
    assert ordered_list[0]['quantity'] == 2
    ordered_list.clear()


def test_buy_with_result():
    market_status = MarketStatus()
    market_status.status = MarketStatus.IN_MARKET
    bs = BuyStage(None, market_status, 10000)

    ba = {'first_ask_price': 6050,
            'second_ask_price': 6060,
            'third_ask_price': 6070,
            'first_ask_remain': 1,
            'second_ask_remain': 1,
            'third_ask_remain': 1}
    bs.ba_data_handler('A005930', ba)
    ordered_list = mock_stock_api.order_list

    assert len(ordered_list) == 1
    assert ordered_list[0]['price'] == 6050
    assert ordered_list[0]['quantity'] == 1
    bs.receive_result({'flag': '4', 'order_number': 12345, 'price': 6050, 'quantity': 1})
    assert bs.get_status() == tradestatus.BUY_ORDER_CONFIRM
    bs.receive_result({'flag': '1', 'order_number': 12345, 'price': 6050, 'quantity': 1})
    assert bs.get_status() == tradestatus.BUY_DONE
    ordered_list.clear()
