from pymongo import MongoClient
from datetime import datetime
from morning.config import db

_called_from_test = False

def record_realtime_order_event(result):
    # flag, code, order_number, quantity, price, order_type, total_quantity
    if not _called_from_test:
        trader_db = MongoClient(db.HOME_MONGO_ADDRESS)['trader']
        order = result.copy()
        order['date'] = datetime.now()
        trader_db['order'].insert_one(order)


def record_make_order(code, price, quantity, is_buy):
    if not _called_from_test:
        trader_db = MongoClient(db.HOME_MONGO_ADDRESS)['trader']
        order = dict(date=datetime.now(), flag=0, order_number=0, 
                    code=code, price=price, total_quantity=0, quantity=quantity, 
                    order_type='2' if is_buy else '1')
        trader_db['order'].insert_one(order)


def record_cancel_order(code, cancel_order):
    if not _called_from_test:
        trader_db = MongoClient(db.HOME_MONGO_ADDRESS)['trader']
        order = cancel_order # already copied
        order.pop('order_modify_type', None)
        order['code'] = code
        order['total_quantity'] = 0
        order['flag'] = 0
        trader_db['order'].insert_one(order)
    

def record_modify_order(code, modify_order):
    if not _called_from_test:
        trader_db = MongoClient(db.HOME_MONGO_ADDRESS)['trader']
        order = modify_order # already copied
        order.pop('order_modify_type', None)
        order['code'] = code
        order['total_quantity'] = 0
        order['flag'] = 0
        trader_db['order'].insert_one(order)
