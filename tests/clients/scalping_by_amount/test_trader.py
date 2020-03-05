import pytest

from configs import client_info
client_info.TEST_MODE = True

from clients.scalping_by_amount import tradestatus
from clients.scalping_by_amount.sellstage import SellStage
from clients.scalping_by_amount.buystage import BuyStage
from clients.scalping_by_amount.marketstatus import MarketStatus
from clients.scalping_by_amount import mock_stock_api, price_info
from clients.scalping_by_amount.trader import Trader


def test_init():
    market_status = MarketStatus()
    market_status.status = MarketStatus.IN_MARKET
    code_info = {'yesterday_close': 6000, # 10 ba unit
                'today_open': 6030,
                'is_kospi': False}
    trader = Trader(None, code_info, market_status)
    trader.start()
    assert isinstance(trader.stage, BuyStage)

def test_send_tick():
    market_status = MarketStatus()
    market_status.status = MarketStatus.IN_MARKET
    code_info = {'yesterday_close': 6000, # 10 ba unit
                'today_open': 6030,
                'is_kospi': False}
    trader = Trader(None, code_info, market_status)
    assert trader.balance == 1000000
    trader.start()

    ba = {'first_ask_price': 6050,
            'second_ask_price': 6060,
            'third_ask_price': 6070,
            'first_ask_remain': 100,
            'second_ask_remain': 100,
            'third_ask_remain': 100}
    trader.ba_data_handler('A005930', ba)
    trader.receive_result({'flag': 4, 'order_number': 12345, 'price': 6060, 'quantity': 16})
    trader.receive_result({'flag': 1, 'order_number': 12345, 'price': 6060, 'quantity': 16})
    
    trader.ba_data_handler('A005930', ba)
    assert isinstance(trader.stage, SellStage)

