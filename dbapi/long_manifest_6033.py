from pymongo import MongoClient

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dbapi import config
from utils.store import Store

_COLLECTION = 'long_list'

class LongManifest:
    @staticmethod
    def drop_from_long(account_num, code, db):
        db[_COLLECTION].delete_one({'account_num': account_num, 'code': code})

    @staticmethod
    def add_to_long(account_num, code, name, quantity, price, db):
        db[_COLLECTION].insert_one({
            'code': code,
            'account_num': account_num,
            'name': name,
            'quantity': quantity,
            'sell_available': quantity,
            'price': price
        })



    def __init__(self, account_num):
        self.db = MongoClient(config.MONGO_SERVER).trader
        self.account_num = account_num

    def get_count(self):
        cursor = self.db[_COLLECTION].find({'account_num':self.account_num})
        return cursor.count()

    def get_long_list(self, store=False):
        long_list = []
        cursor = self.db[_COLLECTION].find({'account_num':self.account_num})
        for c in cursor:
            code = c['code']
            name = c['name']
            quantity = c['quantity']
            sell_available = c['sell_available']
            price = c['price']
            all_price = price * quantity
            d = {'code': code, 'name': name, 'quantity': quantity,
                 'sell_available': sell_available, 'price': price,
                 'all_price': all_price}
            long_list.append(d)

            if store:
                Store.RecordLongManifest(d.copy())
        return long_list

    def get_long_codes(self):
        long_codes = []
        cursor = self.db[_COLLECTION].find({'account_num':self.account_num})
        for i in cursor:
            long_codes.append(i['code'])    
        return long_codes

    def insert_long(self, code, name, account_num, sell_available, price):
        self.db[_COLLECTION].insert_one({
            'code': code,
            'account_num': account_num,
            'name': name,
            'quantity': sell_available,
            'sell_available': sell_available,
            'price': price
        })

    def sold(self, code):
        self.db[_COLLECTION].delete_one({'code': code})


    def _insert_long(self, code, name, sell_available, price):
        self.db[_COLLECTION].insert_one({
            'code': code,
            'account_num': 'test',
            'name': name,
            'quantity': sell_available,
            'sell_available': sell_available,
            'price': price
        })


if __name__ == '__main__':
    lm = LongManifest('test')
    db = MongoClient(config.MONGO_SERVER).trader
    db[_COLLECTION].delete_many({'account_num': 'test'})

    lm._insert_long('A005930', 'LGE', 10, 48000)
    lm._insert_long('A005920', 'HI', 2, 49000)

    l = lm.get_long_list()
    assert l[0]['name'] == 'LGE'
    assert l[1]['name'] == 'HI'
    lm.sold('A005930')
    lc = lm.get_long_codes()
    assert lc[0] == 'A005920'
    db[_COLLECTION].delete_many({'account_num': 'test'})
