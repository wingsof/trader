import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sys import platform as _platform
if _platform == 'win32' or _platform == 'win64':
    from winapi import time_manager as tm
else:
    from dbapi import time_manager as tm

from datetime import datetime

class Store:
    DB = None
    STATE_COLLECTION = 'state'
    LONG_MANIFEST = 'long_manifest'
    ORDER = 'order'
    ORDER_RESULT = 'order_result'
    ORDER_REALTIME = 'order_realtime'

    def RecordStateTransit(old_state, new_state, msg=''):
        print(tm.TimeManager.now(), old_state, new_state, msg)

        if Store.DB is not None:
            Store.DB[Store.STATE_COLLECTION].insert_one({
                'date': datetime.now(),
                'OLD': old_state,
                'NEW': new_state,
                'MSG': msg
            })

    def RecordLongManifest(long_item):
        """ careful not to confuse with long_list collections
            long_list collection is dbapi purpose to record 
        d = {'code': code, 'name': name, 'quantity': quantity,
             'sell_available': sell_available, 'price': price,
             'all_price': all_price}
        """
        if Store.DB is not None:
            t = tm.TimeManager.now()
            long_item['date'] = datetime(t.year, t.month, t.day)
            # prevent duplications while testing
            cursor = Store.DB[Store.LONG_MANIFEST].find({
                'date': datetime(t.year, t.month, t.day),
                'code': code
            })

            if cursor.count() is 0:
                print('(LONG_LIST)\t', 'CODE:', long_item['code'], 
                        'NAME:', long_item['name'], 'QUANTITY:', long_item['quantity'])
                Store.DB[Store.LONG_MANIFEST].insert_one(long_item)

    
    def RecordOrder(code, account_num, account_type, price, quantity, is_buy, expected):
        print('(ORDER)\t', tm.TimeManager.now(), code, price, quantity, 'buy:', is_buy)
        if Store.DB is not None:
            Store.DB[Store.ORDER].insert_one({
                'date': tm.TimeManager.now(),
                'code': code,
                'account_num': account_num,
                'account_type': account_type,
                'price': price,
                'quantity': quantity,
                'expected': expected,
                'position': 'BUY' if is_buy else 'SELL'
            })

    def RecordOrderResult(r):
        if Store.DB is not None:
            r['date'] = tm.TimeManager.now()
            Store.DB[Store.ORDER_RESULT].insert_one(r)
            print('(ORDER RESULT)\t', 'ORDER_ID:', r['order_num'], 'TYPE_CODE:', r['type_code'],
                    'CODE:', r['code'], 'QUANTITY:', r['quantity'],
                    'PRICE:', r['price'], 'ORDER TYPE:', r['order_type'])

    def RecordRealtimeResult(r):
        if Store.DB is not None:
            r['date'] = tm.TimeManager.now()
            Store.DB[Store.ORDER_REALTIME].insert_one(r)
            print('(ORDER NOTIFY)\t', 'ORDER_ID:', r['order_num'], 'FLAG:', r['flag'],
                    'CODE:', r['code'], 'QUANTITY:', r['quantity'], 'PRICE:', r['price'],
                    'TOTAL_QUANTITY:', r['total_quantity'])
