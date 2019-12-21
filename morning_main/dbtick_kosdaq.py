import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt5.QtCore import QCoreApplication
from datetime import datetime
import signal

from morning.logging import logger
from morning.trader import Trader

from morning.account.fake_account import FakeAccount
from morning.pipeline.chooser.cybos.db.stock_search_bull_chooser import StockearchBullChooser
from morning.pipeline.converter.cybos.stock.tick import StockTickConverter
from morning.pipeline.filter.in_market import InMarketFilter
from morning.pipeline.filter.drop_data import DropDataFilter
from morning.pipeline.decision.bool_and_decision import BoolAndDecision
from morning.pipeline.strategy.stock.realtime_minute_suppressed import RealtimeMinuteSuppressed

from morning.pipeline.stream.cybos.stock.db.tick import DatabaseTick


def start_trading(code, account):
    trader = Trader(code, True)
    pipeline = {'name': 'kosdaq_bull',
                'stream': DatabaseTick(datetime(2019, 12, 17), datetime(2019, 12, 18), True),
                'converter': StockTickConverter(),
                'filter': [InMarketFilter(), DropDataFilter(1)],
                'strategy': [RealtimeMinuteSuppressed()],
                'decision': BoolAndDecision(1, 1)} # trade count = 2
    trader.add_pipeline(pipeline)
    trader.set_account(account)
    trader.start_trading()

    return trader


app = None
clients_count = 0

def decrement_thread_count():
    global clients_count
    clients_count -= 1
    if clients_count == 0:
        app.quit()

if __name__ == '__main__':
    app = QCoreApplication(sys.argv)
    logger.setup_main_log()
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    traders = []
    ksbc = StockSearchBullChooser(StockSearchBullChooser.KOSDAQ,
                                datetime(2019, 12, 17).date(), True) # not use database to search codes
    print(ksbc.codes)
    #ksbc.codes = ['A091990']#, 'A078130', 'A097520', 'A225430', 'A082800', 'A238120']
    ksbc.codes = ['A005290']
    account = FakeAccount()
    account.set_date(datetime(2019, 12, 17).date())
    clients_count = len(ksbc.codes)
    for code in ksbc.codes:
        traders.append(start_trading(code, account))
        traders[-1].finished.connect(decrement_thread_count)

    app.exec()
    account.summary()
    logger.exit_main_log()
