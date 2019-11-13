import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pymongo import MongoClient
import pymongo
import time
from PyQt5.QtCore import QCoreApplication, QTimer, QThread
from multiprocessing import Process, Queue

from trade_launcher import TradeLauncher

from sys import platform as _platform
if _platform == 'win32' or _platform == 'win64':
    from winapi import config
    from winapi import connection
    from winapi import trade_util
    from winapi import balance_5331a as balance
    from winapi import cp7043
else:
    from dbapi import config
    from dbapi import connection
    from dbapi import trade_util
    from dbapi import balance_5331a as balance
    from dbapi import cp7043

class Trader:
    def __init__(self):
        self.codes = []

    def get_db_connection(self):
        try:
            MongoClient(config.MONGO_SERVER)
        except pymongo.errors.ConnectionFailure as e:
            print('Could not connect to server:', e)
            return False
        return True

    def _reset(self):
        pass

    def ready(self):
        self._reset()

        conn = connection.Connection()
        if not conn.is_connected():
            print('Network not connected', flush=True)
            return False

        if not self.get_db_connection():
            print('Cannot connect to Mongo')
            return False

        self.trade_util = trade_util.TradeUtil()
        self.account_num = self.trade_util.get_account_number()
        self.account_type = self.trade_util.get_account_type()
        self.balance = balance.get_balance(self.account_num, self.account_type)
        print('Account Num', self.account_num, 'Account Type', self.account_type)
        if len(self.account_num) > 0 and len(self.account_type) > 0:
            pass
        else:
            print('Account is not correct')
            return False

        cp7043.Cp7043().request(self.codes)
        if len(self.codes) == 0:
            print('CODE LOAD failed')
            return False

        return True
    
    def start(self):
        self.trade_launcher = TradeLauncher(self.codes)
        self.trade_launcher.set_account_info(self.account_num, self.account_type, self.balance)
        self.trade_launcher.launch()
            

if __name__ == '__main__':
    if _platform == 'win32' or _platform == 'win64':
        conn = connection.Connection()
        while not conn.is_connected():
            time.sleep(5)

    app = QCoreApplication(sys.argv)
    trader = Trader()
    if not trader.ready():
        print('Not satisfied conditions', flush=True)
        sys.exit(1)

    trader.start()
    app.exec()