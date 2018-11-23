import win32com.client

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.store import Store

class LongManifest:
    def __init__(self, account_num):
        self.account_num = account_num

    def get_count(self):
        self.stock_obj = win32com.client.Dispatch('CpTrade.CpTd6033')
        self.stock_obj.SetInputValue(0, self.account_num)
        self.stock_obj.SetInputValue(1, '1')
        self.stock_obj.SetInputValue(2, 50)
        self.stock_obj.BlockRequest()
        return self.stock_obj.GetHeaderValue(7)

    def get_long_list(self):
        self.stock_obj = win32com.client.Dispatch('CpTrade.CpTd6033')
        self.stock_obj.SetInputValue(0, self.account_num)
        self.stock_obj.SetInputValue(1, '1')
        self.stock_obj.SetInputValue(2, 50)
        self.stock_obj.BlockRequest()

        long_list = []
        for i in range(self.stock_obj.GetHeaderValue(7)):
            code = self.stock_obj.GetDataValue(12, i)
            name = self.stock_obj.GetDataValue(0, i)
            quantity = self.stock_obj.GetDataValue(7, i)
            sell_available = self.stock_obj.GetDataValue(15, i)
            price = self.stock_obj.GetDataValue(17, i)
            all_price = price * quantity
            d = {'code': code, 'name': name, 'quantity': quantity,
                 'sell_available': sell_available, 'price': price,
                 'all_price': all_price}
            long_list.append(d)
            Store.RecordLongManifest(d.copy())

        return long_list

    def get_long_codes(self):
        self.stock_obj = win32com.client.Dispatch('CpTrade.CpTd6033')
        self.stock_obj.SetInputValue(0, self.account_num)
        self.stock_obj.SetInputValue(1, '1')
        self.stock_obj.SetInputValue(2, 50)
        self.stock_obj.BlockRequest()

        long_codes = []
        for i in range(self.stock_obj.GetHeaderValue(7)):
            code = self.stock_obj.GetDataValue(12, i)
            long_codes.append(long_codes)

        return long_codes
