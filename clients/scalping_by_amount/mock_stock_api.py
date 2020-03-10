from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))


order_list = []
modify_order_list = []
cancel_order_list = []
balance = 1000000

def order_stock(reader, code, price, quantity, is_buy):
    order_list.append({'code': code, 'price': price,
            'quantity': quantity, 'is_buy': is_buy})
    return {'status': 0, 'msg': 'OK'}

def modify_order(reader, order_num: int, code, price):
    modify_order_list.append({'order_num': order_num, 'code': code, 'price': price})
    return {'order_number': order_num + 100}


def cancel_order(reader, order_num: int, code, amount): # quantity
    cancel_order_list.append({'order_num': order_num, 'code': code, 'quantity': amount})
    return {'status': 0, 'msg': 'OK'}

def subscribe_stock_bidask(reader, code, ba_data_handler):
    pass


def get_balance(reader):
    return {'balance': balance}


def clear_all():
    order_list.clear()
    modify_order_list.clear()
    cancel_order_list.clear()