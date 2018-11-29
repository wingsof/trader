import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pymongo import MongoClient
import string
import random
from dbapi import config
from dbapi import balance_5331a as balance
from dbapi.long_manifest_6033 import LongManifest
from dbapi import stock_code

class Td0311:
    def __init__(self, obj_id):
        self.obj_id = obj_id
        self.order_type = ''
        self.account_num = ''
        self.account_type = ''
        self.code = ''
        self.quantity = 0
        self.price = 0

    def SetInputValue(self, index, value):
        if index == 0:
            self.order_type = value
        elif index == 1:
            self.account_num = value
        elif index == 2:
            self.account_type = value
        elif index == 3:
            self.code = value
        elif index == 4:
            self.quantity = value
        elif index == 5:
            self.price = value


    def BlockRequest(self):
        db = MongoClient(config.MONGO_SERVER).trader
        if self.order_type == '2': # buy
            b = balance.get_balance(self.account_num, self.account_type)
            print('<<<< BUY ', 'BALANCE:', b, 'PRICE*QUANTITY:', self.quantity * self.price)

            b -= self.quantity * self.price
            balance.update_balance(self.account_num, b)
            print('BUY >>>>', 'FINAL:', b)

            LongManifest.add_to_long(
                    self.account_num, self.code,
                    stock_code.code_to_name(self.code),
                    self.quantity, self.price, db)
        else: # sell
            b = balance.get_balance(self.account_num, self.account_type)
            print('<<<< SELL ', 'BALANCE:', b, 'PRICE*QUANTITY:', self.quantity * self.price)

            b += self.quantity * self.price
            balance.update_balance(self.account_num, b)
            print('SELL >>>>', 'FINAL:', b)

            LongManifest.drop_from_long(self.account_num, self.code, db) 


    def id_generator(self, size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def GetHeaderValue(self, index):
        if index == 0:
            return '0'
        elif index == 1:
            return self.account_num
        elif index == 2:
            return self.account_type
        elif index == 3:
            return self.code
        elif index == 4:
            return self.quantity
        elif index == 5:
            return self.price
        elif index == 8:
            return self.id_generator()
        elif index == 9:
            return 'nnnlife'
        elif index == 10:
            return 'myname'
        elif index == 12:
            return 'order_type'
        return 0
