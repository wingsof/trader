import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pymongo import MongoClient

from dbapi import balance_5331a as balance
from dbapi import td0311_mock as td0311
from dbapi import config
from utils.store import Store

class Order:
    BALANCE_DIVIDER = 20.
    """
    LONG DICT TYPE
        [{'code': code, 'name': name, 'quantity': quantity,
         'sell_available': sell_available, 'price': price,
         'all_price': all_price}, ...]
    """
    def __init__(self, long_list, account_num, account_type):
        self.order_result_list = []
        self.long_list = long_list
        self.account_num = account_num
        self.account_type = account_type
        cash = balance.get_balance(account_num, account_type)
        all_asset = cash + self.get_long_total_price()
        print('cash', cash, 'stock', self.get_long_total_price())
        if all_asset / Order.BALANCE_DIVIDER > cash:
            self.balance = cash
        else:
            self.balance = all_asset / Order.BALANCE_DIVIDER

    def process(self, code, quantity, account_num, account_type, price, is_buy, expected = 0):
        if quantity == 0:
            print("Failed")
        else:
            if is_buy:
                Store.RecordOrder(code, account_num,
                        account_type, price, quantity, is_buy, expected)
            else:
                p = price / self.get_bought_price(code) * 100.
                Store.RecordOrder(code, account_num,
                        account_type, price, quantity, is_buy, p)

            self.obj = td0311.Td0311('CpTrade.CpTd0311')
            order_type = '2' if is_buy else '1'
            self.obj.SetInputValue(0, order_type)
            self.obj.SetInputValue(1, account_num)
            self.obj.SetInputValue(2, account_type)
            self.obj.SetInputValue(3, code)
            self.obj.SetInputValue(4, quantity)
            self.obj.SetInputValue(5, price)
            self.obj.BlockRequest()

            self.order_result_list.append({
                'type_code': self.obj.GetHeaderValue(0),
                'account_num': self.obj.GetHeaderValue(1),
                'account_type': self.obj.GetHeaderValue(2),
                'code': self.obj.GetHeaderValue(3),
                'quantity': self.obj.GetHeaderValue(4),
                'price': self.obj.GetHeaderValue(5),
                'order_num': self.obj.GetHeaderValue(8),
                'account_name': self.obj.GetHeaderValue(9),
                'name': self.obj.GetHeaderValue(10),
                'order_type': self.obj.GetHeaderValue(12),
                'expected': expected
            })

    def get_available_sell_quantity(self, code):
        for l in self.long_list:
            if l['code'] == code:
                return l['quantity']
        return 0

    def get_bought_price(self, code):
        for l in self.long_list:
            if l['code'] == code:
                return l['price']
        return 0

    def get_long_total_price(self):
        total = 0
        for l in self.long_list:
            total += l['price'] * l['quantity']
        return total

    def process_buy_order(self, buy_dict):
        # [expected, price]
        sorted_by_price = sorted(buy_dict.items(), key=lambda kv: kv[1][1])
        final_buy = []
        default_price = 0
        for k, v in sorted_by_price:
            if v[1] == 0 or default_price + v[1] > self.balance: continue
            
            default_price += v[1]
            final_buy.append((k,v))

        quantities = [1] * len(final_buy)

        def get_prices(item, q):
            prices = []
            for i, p in enumerate(item):
                prices.append(q[i] * p[1][1])
            return prices

        def is_over_limit(item, q, limit):
            total = 0
            for i, p in enumerate(item):
                total += p[1][1] * q[i]
            if total > limit:
                return True
            return False

        def add_quantity(item, q):
            qcopy = q.copy()
            prices = get_prices(item, qcopy)
            index = prices.index(min(prices))
            qcopy[index] += 1
            if is_over_limit(item, qcopy, self.balance): return False
            else:
                q[:] = qcopy
                return True

        while add_quantity(final_buy, quantities): pass

        for i, item in enumerate(final_buy): 
            self.process(item[0], quantities[i], self.account_num, self.account_type, item[1][1], True, item[1][0])

    def process_sell_order(self, sell_dict):
        keys = list(sell_dict)
        for k in keys:
            if sell_dict[k][1] == 0:
                continue
            self.process(k, self.get_available_sell_quantity(k), 
                    self.account_num, self.account_type, sell_dict[k][1], False)

    def set_result(self, result):
        pass

    def stop(self):
        pass


if __name__ == '__main__':
    l = [{'code': 'A005930', 'name': 'samsung', 'quantity': 10,
         'sell_available': 10, 'price': 10000,
         'all_price': 10 * 10000}]
    order = Order(l, 'test-account', 'test-type')
    print(order.balance)
    buy_d = {}
    buy_d['A000'] = [105, 0]
    buy_d['A001'] = [105, 100]
    buy_d['A002'] = [105, 200]
    buy_d['A003'] = [105, 300]
    buy_d['A004'] = [105, 400]
    buy_d['A005'] = [105, 500]
    order.process_buy_order(buy_d)
