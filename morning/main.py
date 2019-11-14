import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pymongo import MongoClient
import pymongo
import time
from PyQt5.QtCore import QCoreApplication, QTimer, QThread
from multiprocessing import Process, Queue

from morning.chooser import kosdaq_current_bull_codes
from morning.account import cybos_account, fake_account
from trader import Trader

is_simulation = True

if is_simulation:
    from dbapi import connection
    from dbapi import config
else:
    from winapi import connection
    from winapi import config


if __name__ == '__main__':
    if not is_simulation:
        conn = connection.Connection()
        while not conn.is_connected():
            time.sleep(5)

    trader = Trader(is_simulation)
    if not trader.ready():
        print('Not satisfied conditions', flush=True)
        sys.exit(1)

    trader.set_selector(
        kosdaq_current_bull_codes.KosdaqCurrentBullCodes(is_repeat=True, repeat_msec=60000))

    if is_simulation:
        trader.set_executor(cybos_account.CybosAccount())
    else:
        trader.set_executor(fake_account.FakeAccount())

    # TODO: use converters are over-engineering?
    # Naming Rule : API Provider + Financial Type + Stream Type

    # TODO: how to provide the datetime?
    csr = CybosStockRealtime()
    csbr = CybosStockBaRealtime()
    trader.set_stream_pipeline(csr, csbr)

    """
        trader = Trader(True)
    # selector 는 실시간으로 항목을 추가할 수 있다
    trader.set_selector(KosdaqCurrentBullCodes(True, 60000))

    trader.set_executor(CybosAccount())

    # 스트림 간 동기화 어떻게 맞출 것인가? 시작시간, 종료시간 -> Main Clock은 다음 같이 연결된 Pipeline에 시간을 제공해야 한다
    # 마지막 data stream 인지 어떻게 알릴 것인가?
    # 아래 경우, 스트림 output 은 2개로 나온다
    trader.set_stream_pipeline([(CybosStockRealtime.name, CybosStockRealtimeConverter.name),
                                (CybosStockBaRealtime.name, CybosStockBaRealtimeConverter.name)])

    # 스트림에서는 하나의 데이터만 나올 수 있고, 필터를 거치고 나서는 배열로 나온다
    trader.set_filter_pipeline(0, CybosInMarketRemoveFirstFilter.name, CybosStockRealtimeMinBuffer.name)
    trader.set_filter_pipeline(1, [CybosStockBaInMarketFilter.name])

    trader.set_strategy_pipeline(0, [TickCybosThreeMinUp.name, TickCybosBuySellAccDiff.name], CybosAndDecision.name)
    trader.set_strategy_pipeline(1, [TickCybosDecisionByTakeLast.name])

    trader.set_decision(MongoStockRealRecord.name)
    
    trader.run()
    """

"""
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
    
    def run(self):
        self.trade_launcher = TradeLauncher(self.codes)
        self.trade_launcher.set_account_info(self.account_num, self.account_type, self.balance)
        self.trade_launcher.launch()
"""   