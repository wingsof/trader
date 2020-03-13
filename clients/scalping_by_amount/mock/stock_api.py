from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))

import gevent
from clients.scalping_by_amount.mock import datetime
from clients.scalping_by_amount import tick_analysis
from clients.scalping_by_amount import time
from datetime import timedelta
import pandas as pd

current_order_number = 111111
balance = 10000000
trade_handlers = []
tick_handlers = dict()
ba_tick_handlers = dict()
order_wait_queue = []
current_stocks = dict()
stocks_sheet = []
OUT_BASE = os.environ['MORNING_PATH'] + os.sep + 'output' + os.sep + 'my_tick'

def create_directory(path):
    if not os.path.exists(path):
        os.mkdir(path)


def get_order_num():
    global current_order_number
    order_num = current_order_number
    current_order_number += 1
    return order_num


def is_order_in_queue(order_num):
    for order in order_wait_queue:
        if order['order_number'] == order_num:
            return True
    return False


def remove_stock(code, price, quantity):
    if code not in current_stocks:
        print('ERROR cannot not be in current_stocks when remove') 
        return
    current_stocks[code]['sell'].append((datetime.now(), price, quantity))
    buy_quantity = current_stocks[code]['buy'][2]
    sell_quantity = sum([d[2] for d in current_stocks[code]['sell']])
    if buy_quantity == sell_quantity:
        buy_record = current_stocks[code]['buy']
        sell_record = current_stocks[code]['sell']
        stocks_sheet.append({'time': buy_record[0], 'code': code, 'type': 'buy', 'price': buy_record[1], 'quantity': buy_record[2], 'profit': ''})

        total_sell_amount = sum([s[1] * s[2] for s in sell_record]) * 0.9975
        total_buy_amount = buy_record[1] * buy_record[2]
        profit = (total_sell_amount - total_buy_amount) / total_buy_amount * 100
        for i, sr in enumerate(sell_record):
            record = {'time': sr[0], 'code': code, 'type': 'sell', 'price': sr[1], 'quantity': sr[2], 'profit': ''}
            if i == len(sell_record) - 1:
                record['profit'] = str(float("{0:.2f}".format(profit)))
            stocks_sheet.append()
        current_stocks.pop(code, None)


def out_stocks_sheet():
    current_code = ''
    buy_datetime_arr = []
    sell_datetime_arr = []
    buy_prices = []
    sell_prices = []
    create_directory(OUT_BASE)
    for ss in stocks_sheet:
        if current_code != ss['code']:
            if len(buy_datetime_arr) > 0:
                tick_analysis.start_tick_analysis(current_code,
                                                    buy_datetime_arr,
                                                    sell_datetime_arr,
                                                    buy_prices,
                                                    sell_prices, OUT_BASE)
            buy_datetime_arr.clear()
            sell_datetime_arr.clear()
            buy_prices.clear()
            sell_prices.clear()
        if ss['type'] == 'buy':
            buy_datetime_arr.append(ss['time'])
            buy_prices.append(ss['price'])
        else:
            sell_datetime_arr.append(ss['time'])
            sell_prices.append(ss['price'])
        current_code = ss['code']
         
    if len(stocks_sheet) > 0:
        pd.DataFrame(stocks_sheet).to_excel(OUT_BASE + os.sep + 'trade_sheet.xlsx')


def add_stock(code, price, quantity):
    if code in current_stocks:
        print('ERROR cannot be in current_stocks when add')

    current_stocks[code] = {'buy':(datetime.now(), price, quantity), 'sell': []}


def set_current_first_bid(code, price):
    global balance
    done_order = []
    for order in order_wait_queue:
        if order['code'] == code and order['order_type'] == '1' and (order['flag'] == '4' or order['flag'] == '2'):
            if order['price'] <= price:
                done_order.append(order)
                send_to_trade_handlers({'flag': '1',
                                        'code': order['code'],
                                        'quantity': order['quantity'],
                                        'price': price,
                                        'order_type': '1',
                                        'order_number': order['order_number'],
                                        'total_quantity': 0})
                balance += order['price'] * order['quantity'] * 0.997
                remove_stock(code, order['price'], order['quantity'])            
    for order in done_order:
        order_wait_queue.remove(order)
                

def send_to_trade_handlers(result):
    for handler in trade_handlers:
        handler(result)


def send_order_confirm_result(code, price, quantity, is_buy, order_time):
    global balance
    time.sleep(1)
    order_num = get_order_num()
    print('order_number', order_num)
    confirm_response = {'flag': '4',
                        'code': code,
                        'quantity': quantity,
                        'order_number': order_num,
                        'price': price,
                        'order_type': ('2' if is_buy else '1'),
                        'total_quantity': 0}
    send_to_trade_handlers(confirm_response)
    if is_buy:
        result = {'flag': '1',
                'code': code,
                'quantity': quantity,
                'order_number': order_num,
                'price': price,
                'order_type': '2',
                'total_quantity': quantity}
        balance  -= price * quantity
        add_stock(code, price, quantity)
        send_to_trade_handlers(result)
    else:
        order_wait_queue.append(confirm_response)


def send_modify_confirm_result(order_num, code, price, quantity, order_type, order_time):
    time.sleep(0)
    # Actually first should send flag '4' but not essential
    result = {'flag': '2',
                'code': code,
                'quantity': quantity,
                'order_number': order_num,
                'price': price,
                'order_type': order_type,
                'total_quantity': 0}
    send_to_trade_handlers(result)


def send_cancel_confirm_result(order_num, code, price, quantity, order_type, order):
    time.sleep(3)
    # Actually first should send flag '4' but not essential
    result = {'flag': '2',
                'code': code,
                'quantity': quantity,
                'order_number': order_num,
                'price': price,
                'order_type': order_type,
                'total_quantity': 0}
    order_wait_queue.remove(order)


def order_stock(reader, code, price, quantity, is_buy):
    gevent.spawn(send_order_confirm_result, code, price, quantity, is_buy, datetime.now())
    return {'status': 0, 'msg': 'OK'}


def modify_order(reader, order_num: int, code, price):
    print('process modify_order', order_num, code, price)
    previous_order = None
    for order in order_wait_queue:
        if order['order_number'] == order_num and order['code'] == code:
            previous_order = order
            break

    if previous_order is None:
        print('*' * 100, 'ERROR')
        return
    
    new_num = get_order_num()
    previous_order['order_number'] = new_num
    previous_order['flag'] = '2'
    previous_order['price'] = price

    gevent.spawn(send_modify_confirm_result, new_num, code, price, previous_order['quantity'], previous_order['order_type'], datetime.now())
    return {'order_number': new_num}


def cancel_order(reader, order_num: int, code, amount): # quantity
    previous_order = None
    for order in order_wait_queue:
        if order['order_number'] == order_num and order['code'] == code:
            previous_order = order
            break

    if previous_order is None:
        print('*' * 100, 'ERROR')
        return
    
    new_num = get_order_num()    
    previous_order['order_number'] = new_num
    previous_order['flag'] = '2'
    previous_order['price'] = price

    gevent.spawn(send_cancel_confirm_result, new_num, code, price, previous_order['quantity'], previous_order['order_type'], previous_order)
    return {'status': 0, 'msg': 'OK'}


def subscribe_stock(reader, code, tick_data_handler):
    print('subscribe stock', code)
    if code in tick_handlers:
        tick_handlers[code].append(tick_data_handler)
    else:
        tick_handlers[code] = [tick_data_handler]


def subscribe_stock_bidask(reader, code, ba_data_handler):
    print('subscribe bidask', code)
    if code in ba_tick_handlers:
        ba_tick_handlers[code].append(ba_data_handler)
    else:
        ba_tick_handlers[code] = [ba_data_handler]


def send_bidask_data(code, tick):
    if code in ba_tick_handlers:
        for handler in ba_tick_handlers[code]:
            gevent.spawn(handler, code, [tick])


def send_tick_data(code, tick):
    if code in tick_handlers:
        for handler in tick_handlers[code]:
            gevent.spawn(handler, code, [tick])


def get_balance(reader):
    return {'balance': balance}


def subscribe_alarm(reader, handler):
    pass


def subscribe_trade(reader, handler):
    trade_handlers.append(handler)
