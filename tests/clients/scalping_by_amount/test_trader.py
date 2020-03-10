import pytest

from configs import client_info
client_info.TEST_MODE = True

from clients.scalping_by_amount import tradestatus
from clients.scalping_by_amount.sellstage import SellStage
from clients.scalping_by_amount.buystage import BuyStage
from clients.scalping_by_amount.marketstatus import MarketStatus
from clients.scalping_by_amount import mock_stock_api, price_info
from clients.scalping_by_amount.trader import Trader
from clients.common import morning_client
from morning_server import message

mock_stock_api.balance = 1000000
invest_money = mock_stock_api.balance / Trader.BALANCE_DIVIDER

def down_bidask(bidask_table):
    keys = ['first_ask_price', 'second_ask_price', 'third_ask_price', 'fourth_ask_price', 'fifth_ask_price',
            'first_bid_price', 'second_bid_price', 'third_bid_price', 'fourth_bid_price', 'fifth_bid_price']
    for k in keys:
        price = bidask_table[k]
        unit = morning_client.get_ask_bid_price_unit(message.KOSDAQ, price-1)
        bidask_table[k] = price - unit
    

def get_trader(code_info, market_status):
    trader = Trader(None, code_info, market_status)
    trader.start()
    return trader


def test_start(default_code_info, in_market_status):
    trader = get_trader(default_code_info, in_market_status)
    assert isinstance(trader.stage, BuyStage)


def test_case_1_1(default_code_info, in_market_status, default_bidask):
    trader = get_trader(default_code_info, in_market_status)
    trader.ba_data_handler('A005930', default_bidask)
    
    assert isinstance(trader.stage, BuyStage)
    assert trader.stage.get_status() == tradestatus.BUY_ORDER_SEND_DONE
    trader.receive_result({'flag': '4', 'order_number': 12345, 'price': 6060, 'quantity': int(invest_money/6060)})
    assert trader.stage.get_status() == tradestatus.BUY_ORDER_CONFIRM
    trader.receive_result({'flag': '1', 'order_number': 12345, 'price': 6070, 'quantity': int(invest_money/6060)})
    assert trader.stage.get_status() == tradestatus.BUY_DONE
    trader.ba_data_handler('A005930', default_bidask)
    assert isinstance(trader.stage, SellStage)
    mock_stock_api.clear_all()

def test_buy_some(default_code_info, in_market_status, default_bidask):
    trader = get_trader(default_code_info, in_market_status)
    trader.ba_data_handler('A005930', default_bidask)
    assert isinstance(trader.stage, BuyStage)
    assert trader.stage.get_status() == tradestatus.BUY_ORDER_SEND_DONE
    trader.receive_result({'flag': '4', 'order_number': 12345, 'price': 6050, 'quantity': int(invest_money/6050)})
    assert trader.stage.get_status() == tradestatus.BUY_ORDER_CONFIRM
    trader.receive_result({'flag': '1', 'order_number': 12345, 'price': 6050, 'quantity': int(invest_money/6050) - 1})
    assert trader.stage.get_status() == tradestatus.BUY_SOME
    trader.receive_result({'flag': '1', 'order_number': 12345, 'price': 6050, 'quantity': 1})
    assert trader.stage.get_status() == tradestatus.BUY_DONE
    mock_stock_api.clear_all()

def test_buy_some_with_cancel(default_code_info, in_market_status, default_bidask):
    trader = get_trader(default_code_info, in_market_status)
    trader.ba_data_handler('A005930', default_bidask)
    assert isinstance(trader.stage, BuyStage)
    assert trader.stage.get_status() == tradestatus.BUY_ORDER_SEND_DONE
    trader.receive_result({'flag': '4', 'order_number': 12345, 'price': 6050, 'quantity': int(invest_money/6050)})
    assert trader.stage.get_status() == tradestatus.BUY_ORDER_CONFIRM
    trader.receive_result({'flag': '1', 'order_number': 12345, 'price': 6050, 'quantity': int(invest_money/6050)-1})
    assert trader.stage.get_status() == tradestatus.BUY_SOME
    trader.ba_data_handler('A005930', default_bidask)
    assert len(mock_stock_api.cancel_order_list) == 1
    assert mock_stock_api.cancel_order_list[0]['quantity'] == 1
    trader.receive_result({'flag': '4', 'order_number': 12345, 'price': 6050, 'quantity': 1})
    trader.receive_result({'flag': '2', 'order_number': 12345, 'price': 6050, 'quantity': 1})
    assert trader.stage.get_status() == tradestatus.BUY_DONE
    mock_stock_api.clear_all()

def test_buy_some_with_buy_success(default_code_info, in_market_status, default_bidask):
    trader = get_trader(default_code_info, in_market_status)
    trader.ba_data_handler('A005930', default_bidask)
    assert isinstance(trader.stage, BuyStage)
    assert trader.stage.get_status() == tradestatus.BUY_ORDER_SEND_DONE
    trader.receive_result({'flag': '4', 'order_number': 12345, 'price': 6050, 'quantity': int(invest_money/6050)})
    assert trader.stage.get_status() == tradestatus.BUY_ORDER_CONFIRM
    trader.receive_result({'flag': '1', 'order_number': 12345, 'price': 6050, 'quantity': int(invest_money/6050)-1})
    assert trader.stage.get_status() == tradestatus.BUY_SOME
    trader.ba_data_handler('A005930', default_bidask)
    assert len(mock_stock_api.cancel_order_list) == 1
    assert mock_stock_api.cancel_order_list[0]['quantity'] == 1
    trader.receive_result({'flag': '4', 'order_number': 12345, 'price': 6050, 'quantity': 1})
    trader.receive_result({'flag': '1', 'order_number': 12345, 'price': 6050, 'quantity': 1})
    trader.receive_result({'flag': '3', 'order_number': 12345, 'price': 6050, 'quantity': 1})
    assert trader.stage.get_status() == tradestatus.BUY_DONE
    mock_stock_api.clear_all()

def test_case_1_2(default_code_info, in_market_status, default_bidask):
    trader = get_trader(default_code_info, in_market_status)
    ba = default_bidask.copy()
    trader.ba_data_handler('A005930', ba)
    assert trader.stage.get_status() == tradestatus.BUY_ORDER_SEND_DONE
    down_bidask(ba) # 6030
    trader.ba_data_handler('A005930', ba)
    assert trader.stage.get_status() == tradestatus.BUY_ORDER_SEND_DONE
    assert len(mock_stock_api.modify_order_list) == 0
    down_bidask(ba) # 6020
    trader.ba_data_handler('A005930', ba)
    assert trader.stage.get_status() == tradestatus.BUY_ORDER_SEND_DONE
    assert len(mock_stock_api.modify_order_list) == 0
    trader.receive_result({'flag': '4', 'order_number': 12345, 'price': 6050, 'quantity': int(invest_money/6050)})
    assert trader.stage.get_status() == tradestatus.BUY_ORDER_CONFIRM
    trader.receive_result({'flag': '1', 'order_number': 12345, 'price': 6050, 'quantity': int(invest_money/6050)})
    assert trader.stage.get_status() == tradestatus.BUY_DONE
    assert isinstance(trader.stage, BuyStage)
    trader.ba_data_handler('A005930', ba)
    assert isinstance(trader.stage, SellStage)

    trader.ba_data_handler('A005930', ba)
    assert trader.stage.get_status() == tradestatus.SELL_PROGRESSING
    assert trader.stage.point_price == 6090
    assert mock_stock_api.order_list[-1]['price'] == 6110 # MAX 3 STEP
    quantities = [3, 3, 3, 3, 4]
    for i in range(5): # 6090 is minimum profit ba
        trader.receive_result({'flag': '4', 'order_number': 12346+i, 'price': 6090+i*10, 'quantity': quantities[i]})
    down_bidask(ba) # 6010
    trader.ba_data_handler('A005930', ba)
    assert len(mock_stock_api.modify_order_list) == 0
    
    down_bidask(ba) # 6000
    trader.ba_data_handler('A005930', ba)
    assert len(mock_stock_api.modify_order_list) == 1
    assert mock_stock_api.modify_order_list[0]['price'] == 6000
    down_bidask(ba) # 5990
    trader.ba_data_handler('A005930', ba)
    assert len(mock_stock_api.modify_order_list) == 2
    trader.top_edge_detected()
    assert len(mock_stock_api.modify_order_list) == 5
    assert trader.stage.immediate_sell_price == 5990
    mock_stock_api.clear_all()

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
def default_code_info():
    return {'yesterday_close': 6000, # 10 ba unit
            'today_open': 6030,
            'is_kospi': False,
            'code': 'A005930'}

@pytest.fixture()
def in_market_status():
    market_status = MarketStatus()
    market_status.status = MarketStatus.IN_MARKET
    return market_status
