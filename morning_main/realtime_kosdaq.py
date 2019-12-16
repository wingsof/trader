import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt5.QtCore import QCoreApplication
from datetime import datetime
import signal

from morning.logging import logger

from morning.trader import Trader

from morning.account.cybos_kosdaq_account import CybosKosdaqAccount
from morning.pipeline.chooser.cybos.db.kosdaq_search_bull_chooser import KosdaqSearchBullChooser
from morning.pipeline.converter.cybos.stock.tick import StockTickConverter
from morning.pipeline.filter.in_market import InMarketFilter
from morning.pipeline.filter.drop_data import DropDataFilter
from morning.pipeline.decision.bool_and_decision import BoolAndDecision
from morning.pipeline.strategy.stock.realtime_minute_suppressed import RealtimeMinuteSuppressed

from morning.pipeline.stream.cybos.stock.tick import CybosStockTick


def start_trading(code, account):
    trader = Trader(code)
    pipeline = {'name': 'kosdaq_bull',
                'stream': CybosStockTick(),
                'converter': StockTickConverter(),
                'filter': [InMarketFilter(), DropDataFilter(1)],
                'strategy': [RealtimeMinuteSuppressed()],
                'decision': BoolAndDecision(1, 2)} # trade count = 2
    trader.add_pipeline(pipeline)
    trader.set_account(account)
    trader.run()

    return trader


if __name__ == '__main__':
    app = QCoreApplication(sys.argv)
    logger.setup_main_log()
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    traders = []
    ksbc = KosdaqSearchBullChooser(datetime.now().date(), False) # not use database to search codes
    account = CybosKosdaqAccount()
    for code in ksbc.codes:
        account.set_bidask_monitoring(code)
        traders.append(start_trading(code, account))

    app.exec()
    logger.exit_main_log()
