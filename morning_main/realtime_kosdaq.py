import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt5.QtCore import QCoreApplication, QTimer
from datetime import datetime
import signal

from morning.logging import logger
from morning.cybos_api.connection import Connection

from morning.trader import Trader

from morning.account.cybos_kosdaq_account import CybosKosdaqAccount
from morning.pipeline.chooser.cybos.db.stock_search_bull_chooser import StockSearchBullChooser
from morning.pipeline.converter.cybos.stock.tick import StockTickConverter
from morning.pipeline.filter.in_market import InMarketFilter
from morning.pipeline.filter.drop_data import DropDataFilter
from morning.pipeline.decision.bool_and_decision import BoolAndDecision
from morning.pipeline.strategy.stock.realtime_minute_suppressed import RealtimeMinuteSuppressed

from morning.pipeline.stream.cybos.stock.tick import CybosStockTick
from morning.config import stock_time


def start_trading(code, account):
    trader = Trader(code)
    cst = CybosStockTick()
    pipeline = {'name': 'kosdaq_bull',
                'stream': cst,
                'converter': StockTickConverter(),
                'filter': [InMarketFilter(), DropDataFilter(1)],
                'strategy': [RealtimeMinuteSuppressed()],
                'decision': BoolAndDecision(1, 1)} # trade count = 2
    streams.append(cst)
    trader.add_pipeline(pipeline)
    trader.set_account(account)
    trader.start_trading()

    return trader


def check_finalize_time():
    if (datetime.now().hour >= stock_time.MARKET_CLOSE_HOUR and 
            datetime.now().minute >= stock_time.STOCK_FORCE_COVERING_MINUTE):
        for stream in streams:
            stream.finalize()
        finalize_timer.stop()
    

if __name__ == '__main__':
    conn = Connection()
    if not conn.is_connected():
        print('CYBOS is not connected')
        sys.exit(1)

    app = QCoreApplication(sys.argv)
    logger.setup_main_log()
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    finalize_timer = QTimer()
    finalize_timer.setInterval(1000)
    finalize_timer.timeout.connect(check_finalize_time)
    traders = []
    codes = []
    streams = []
    kosdaq_codes = StockSearchBullChooser(StockSearchBullChooser.KOSDAQ, datetime.now().date(), False) # not use database to search codes
    kospi_codes = StockSearchBullChooser(StockSearchBullChooser.KOSPI, datetime.now().date(), False)
    codes.extend(kosdaq_codes.codes)
    codes.extend(kospi_codes.codes)
    account = CybosKosdaqAccount()
    for code in codes:
        account.set_bidask_monitoring(code)
        traders.append(start_trading(code, account))

    finalize_timer.start()
    app.exec()
    logger.exit_main_log()
