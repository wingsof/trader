import pytest

from configs import client_info
client_info.TEST_MODE = True

from clients.scalping_by_amount import tradestatus
from clients.scalping_by_amount.sellstage import SellStage
from clients.scalping_by_amount.marketstatus import MarketStatus
from clients.scalping_by_amount import mock_stock_api, price_info


def test_init():
    ss = SellStage(None, None, None, 1000, 10)
    assert ss.get_status() == tradestatus.SELL_WAIT


def test_price_slot():
    l = price_info.create_slots(9000, 9500, 9100, False)
    first_vi_index = -1
    for i in range(len(l[0])):
        if l[0][i] == 10000: # actual 10% -> 10010
            first_vi_index = i
            break
    assert l[1][first_vi_index] == price_info.VI_MARK

    second_vi_index = -1
    for i in range(len(l[0])):
        if l[0][i] == 10900: # actual 20% -> 10920
            second_vi_index = i
            break
    assert l[1][second_vi_index] == price_info.VI_MARK

    l = price_info.create_slots(6000, 6050, 6030, False)
    first_vi_index = -1
    for i in range(len(l[0])):
        if l[0][i] == 6630: # actual 10% -> 6633
            first_vi_index = i
            break
    assert l[1][first_vi_index] == price_info.VI_MARK

    second_vi_index = -1
    for i in range(len(l[0])):
        if l[0][i] == 7230: # actual 20% -> 7236
            second_vi_index = i
            break
    assert l[1][second_vi_index] == price_info.VI_MARK



def test_send_first_ba():
    market_status = MarketStatus()
    market_status.status = MarketStatus.IN_MARKET
    code_info = {'yesterday_close': 6000, # 10 ba unit
                'today_open': 6030,
                'is_kospi': False}

    ss = SellStage(None, code_info, market_status, 6050, 10)
    ss.ba_data_handler('A005930', {'first_bid_price': 6060})
    slots = price_info.create_slots(code_info['yesterday_close'],
        ss.current_bid, code_info['today_open'], False)

    assert ss.point_price == 6060
    assert ss.current_bid == 6060
    assert ss.minimum_profit_price == 6050 * 1.0025
    # 6070 is minimum ba
    """
    for i in range(len(slots[0])):
        print(slots[0][i], slots[1][i])
    """
    assert len(slots[0]) > 10
    assert len(price_info.upper_available_empty_slots(slots)) > 10

    price_slot = ss.get_price_slots(slots, ss.minimum_profit_price, 10)
    assert len(price_slot) >= 10
    assert price_slot[0] == 6070

    ordered_list = mock_stock_api.order_list
    assert len(ordered_list) == 10
    start_from = 6070
    for m in ordered_list:
        assert m['price'] == start_from
        assert m['quantity'] == 1
        start_from += 10
    mock_stock_api.order_list.clear()
    assert ss.get_status() == tradestatus.SELL_ORDER_SEND_DONE
    start_price = 6070
    for i in range(10):
        ss.receive_result({'flag': 4, 'order_number': 12345, 'price': start_price, 'quantity': 1})
        start_price += 10

    assert ss.get_status() != tradestatus.SELL_DONE

    start_price = 6070
    for i in range(9):
        ss.receive_result({'flag': 1, 'order_number': 12345, 'price': start_price, 'quantity': 1})
        start_price += 10
    assert ss.get_status() != tradestatus.SELL_DONE

    ss.ba_data_handler('A005930', {'first_bid_price': 6060})
    ss.ba_data_handler('A005930', {'first_bid_price': 6050})
    ss.ba_data_handler('A005930', {'first_bid_price': 6040})
    assert len(mock_stock_api.modify_order_list) == 1
    assert mock_stock_api.modify_order_list[0]['price'] == 6040
