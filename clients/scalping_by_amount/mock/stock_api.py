from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))


current_order_number = 111111
balance = 10000000
order_list = []
modify_order_list = []
cancel_order_list = []
trade_handlers = []
tick_handlers = dict()
ba_tick_handlers = dict()
code_bid_info = dict() # Use keep bid price and send sell result


def increase_order_num():
    global current_order_number
    current_order_number += 1


def send_order_confirm_result(code, price, quantity, is_buy):
    for handler in trade_handlers:
       confirm_response = ({'flag': '4',
                            'code': code,
                            'quantity': quantity,
                            'order_number': current_order_number,
                            'price': price,
                            'order_type': ('2' if is_buy else '1'),
                            'total_quantity': 0})
       if is_buy:
           pass #TODO: send result immediately
    increase_order_num()


def send_modify_confirm_result(order_num, code, price, quantity):
    pass


def order_stock(reader, code, price, quantity, is_buy):
    order_list.append({'code': code, 'price': price,
            'quantity': quantity, 'is_buy': is_buy})
    gevent.spawn(send_order_confirm_result, code, price, quantity, is_buy)
    return {'status': 0, 'msg': 'OK'}


def modify_order(reader, order_num: int, code, price):
    modify_order_list.append({'order_num': order_num, 'code': code, 'price': price})
    gevent.spawn(
    return {'order_number': order_num + 100}


def cancel_order(reader, order_num: int, code, amount): # quantity
    cancel_order_list.append({'order_num': order_num, 'code': code, 'quantity': amount})
    return {'status': 0, 'msg': 'OK'}


def subscribe_stock(reader, code, tick_data_handler):
    if code in tick_handlers:
        tick_handlers[code].append(tick_data_handler)
    else:
        tick_handlers[code] = [tick_data_handler]


def subscribe_stock_bidask(reader, code, ba_data_handler):
    if code in ba_data_handlers:
        ba_data_handlers[code].append(ba_data_handler)
    else:
        ba_data_handlers[code] = [ba_data_handler]


def send_bidask_data(code, tick):
    if code in ba_data_handlers:
        for handler in ba_data_handlers[code]:
            gevent.spawn(handler, code, tick)


def send_tick_data(code, tick):
    if code in tick_handlers:
        for handler in tick_handlers[code]:
            gevent.spawn(handler, code, tick)


def get_balance(reader):
    return {'balance': balance}


def subscribe_alarm(reader, handler):
    pass


def subscribe_trade(reader, handler):
    trade_handlers.append(handler)


def clear_all():
    order_list.clear()
    modify_order_list.clear()
    cancel_order_list.clear()
