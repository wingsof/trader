import sys
from PyQt5.QtCore import QCoreApplication, QTimer
import pymongo
from pymongo import MongoClient
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from utils import profit_calc
from utils import speculation

from sys import platform as _platform
if _platform == 'win32' or _platform == 'win64':
    from winapi import connection, stock_chart, stock_code
    from winapi import balance_5331a as balance
    from winapi import trade_util as tu
    from winapi import long_manifest_6033 as lm
    from winapi import stock_current
    from winapi.time_manager import TimeManager
    from winapi import order_0311 as order
else:
    from dbapi import connection, stock_chart, stock_code
    from dbapi import balance_5331a as balance
    from dbapi import trade_util as tu
    from dbapi import long_manifest_6033 as lm
    from dbapi import stock_current
    from dbapi.time_manager import TimeManager


class Trader:
    NOT_RUNNING = 0
    RUNNING = 1
    ORDER_COLLECT = 2
    ORDER_START = 3
    ORDER_DONE = 4
    ORDER_WAITING = 5
    WAITING = 6

    def __init__(self):
        self.time_manager = TimeManager()
        self.speculation = speculation.Speculation()
        self.heart_beat = QTimer()
        self.heart_beat.timeout.connect(self.time_check)
        self._reset()

    def _reset(self):
        self.status = Trader.NOT_RUNNING
        self.db = None
        self.account_num = ''
        self.account_type = ''
        self.long_manifest = None
        self.long_codes = []
        self.code_list = []
        self.subscriber = None
        self.order = None

    def ready(self):
        self._reset()

        conn = connection.Connection()
        if not conn.is_connected():
            print('Network not connected')
            return False

        self.get_db_connection()
        if self.db == None:
            print('DB Connection failed')
            return False

        self.trade_util = tu.TradeUtil()
        self.account_num = self.trade_util.get_account_number()
        self.account_type = self.trade_util.get_account_type()
        self.long_manifest = lm.LongManifest(self.account_num)

        self.get_long_codes()

        if len(self.account_num) > 0 and len(self.account_type) > 0:
            return True
        return False

    def get_long_codes(self):
        self.long_codes = self.long_manifest.get_long_codes()

        self.code_list = stock_code.get_kospi200_list()
        for c in self.long_codes:
            if c not in self.code_list:
                self.code_list.append(c)

    def subscribe(self):
        self.subscriber = stock_current.StockCurrent(
                self.code_list, self.long_codes, self.speculation.get_speculation(self.time_manager.get_today(), self.code_list))
        self.subscriber.start()

    def unsubscribe(self):
        self.subscriber.stop()

    def get_db_connection(self):
        try:
            client = MongoClient('mongodb://nnnlife.iptime.org:27017')
            self.db = client.trader
        except pymongo.errors.ConnectionFailure as e:
            print('Could not connect to server:', e)
            
    def start(self):
        self.heart_beat.start(self.time_manager.get_heart_beat())

    def time_check(self):
        if self.status == Trader.NOT_RUNNING: # ready is done when first running
            if self.time_manager.is_runnable():
                print('NOT_RUNNING -> RUNNING')
                self.status = Trader.RUNNING
                self.subscribe()
            else:
                print(datetime.now(), 'NOT_RUNNING -> WAITING')
                self.status = Trader.WAITING
        elif self.status == Trader.WAITING:
            if self.time_manager.is_runnable():
                print(datetime.now(), 'WAITING -> RUNNING')
                if not self.ready():
                    print(datetime.now(), 'ERROR OCCURRED')
                    sys.exit(1)
                self.status = Trader.RUNNING
                self.subscribe()
        elif self.status == Trader.RUNNING:
            if self.time_manager.is_order_collect_time():
                print(datetime.now(), 'RUNNING -> ORDER_COLLECT')
                self.status = Trader.ORDER_COLLECT

        elif self.status == Trader.ORDER_COLLECT:
            if self.time_manager.is_order_start_time():
                print(datetime.now(), 'ORDER_COLLECT -> ORDER_START')
                self.status = Trader.ORDER_START
                self.order = order.Order(self.long_manifest.get_long_list())

        elif self.status == Trader.ORDER_START:
            print(datetime.now(), 'ORDER_START -> ORDER_WAITING')
            self.order.process_buy_order(self.subscriber.get_buy_dict())
            self.order.process_sell_order(self.subscriber.get_sell_dict())
            self.status = Trader.ORDER_WAITING    

        elif self.status == Trader.ORDER_WAITING:
            if self.time_manager.is_order_wait_done_time():
                print(datetime.now(), 'ORDER_WAITING -> WAITING')
                self.unsubscribe()
                self.status = Trader.WAITING


if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QCoreApplication(sys.argv)
    trader = Trader()
    if not trader.ready():
        print('Not satisfied conditions')
        sys.exit(1)

    trader.start()
    app.exec()
