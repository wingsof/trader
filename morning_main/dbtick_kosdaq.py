import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt5.QtCore import QCoreApplication
from datetime import datetime
import signal

from morning.logging import logger
from morning.cybos_api.connection import Connection

from morning.trader import Trader

from morning.account.fake_account import FakeAccount
from morning.pipeline.chooser.cybos.db.kosdaq_search_bull_chooser import KosdaqSearchBullChooser
from morning.pipeline.converter.cybos.stock.tick import StockTickConverter
from morning.pipeline.filter.in_market import InMarketFilter
from morning.pipeline.filter.drop_data import DropDataFilter
from morning.pipeline.decision.bool_and_decision import BoolAndDecision
from morning.pipeline.strategy.stock.realtime_minute_suppressed import RealtimeMinuteSuppressed

from morning.pipeline.stream.cybos.stock.db.tick import DatabaseTick


def start_trading(code, account):
    trader = Trader(code, False)
    pipeline = {'name': 'kosdaq_bull',
                'stream': DatabaseTick(datetime(2019, 12, 16), datetime(2019, 12, 17), False)
                'converter': StockTickConverter(),
                'filter': [InMarketFilter(), DropDataFilter(1)],
                'strategy': [RealtimeMinuteSuppressed()],
                'decision': BoolAndDecision(1, 1)} # trade count = 2
    trader.add_pipeline(pipeline)
    trader.set_account(account)
    trader.start_trading()

    return trader


if __name__ == '__main__':
    app = QCoreApplication(sys.argv)
    logger.setup_main_log()
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    traders = []
    ksbc = KosdaqSearchBullChooser(datetime.now().date(), False) # not use database to search codes
    account = FakeAccount()
    account.set_date(datetime.now().date())
    for code in ksbc.codes:
        traders.append(start_trading(code, account))

    app.exec()
    account.summary()
    logger.exit_main_log()
