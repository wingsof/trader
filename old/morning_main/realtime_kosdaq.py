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
from morning.cybos_api.cp7043 import Cp7043
from morning.pipeline.converter.cybos.stock.tick import StockTickConverter
from morning.pipeline.filter.in_market import InMarketFilter
from morning.pipeline.filter.drop_data import DropDataFilter
from morning.pipeline.decision.bool_and_decision import BoolAndDecision
from morning.pipeline.strategy.stock.realtime_minute_suppressed import RealtimeMinuteSuppressed

from morning.pipeline.stream.cybos.stock.tick import CybosStockTick
from morning.config import stock_time


def check_finalize_time():
    logger.print('check_finalize_time')
    if (datetime.now().hour >= stock_time.MARKET_CLOSE_HOUR and 
            datetime.now().minute >= stock_time.STOCK_FORCE_COVERING_MINUTE):
        for stream in streams:
            stream.finalize()
        finalize_timer.stop()


def find_bull_codes():
    logger.print('find_bull_codes')
    # check holidays
    now = datetime.now()
    year, month, day = now.year, now.month, now.day
    if datetime(year, month, day, 8, 50) <= now <= datetime(year, month, day, 14, 0):
        if len(current_subscribe_codes) * 2 >= 400:
            return

        bull_codes = []
        kospi_cp = Cp7043(Cp7043.KOSPI)
        kosdaq_cp = Cp7043(Cp7043.KOSDAQ)
        kospi_codes = []
        kosdaq_codes = []
        kospi_cp.request(kospi_codes)
        kosdaq_cp.request(kosdaq_codes)
        bull_codes.extend(kospi_codes)
        bull_codes.extend(kosdaq_codes)
        code_diff = set(bull_codes).difference(current_subscribe_codes)
        logger.print('code diff', code_diff)
        for code in code_diff:
            if len(current_subscribe_codes) * 2 >= 400:
                break
            current_subscribe_codes.update({code})
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
            account.set_bidask_monitoring(code)
            trader.start_trading()
            traders.append(trader)


if __name__ == '__main__':
    conn = Connection()
    if not conn.is_connected():
        print('CYBOS is not connected')
        sys.exit(1)

    app = QCoreApplication(sys.argv)
    logger.setup_main_log()
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    finalize_timer = QTimer()
    finalize_timer.setInterval(10000)
    finalize_timer.timeout.connect(check_finalize_time)
    bull_timer = QTimer()
    bull_timer.setInterval(60000)
    bull_timer.timeout.connect(find_bull_codes)
    traders = []
    codes = []
    streams = []
    current_subscribe_codes = set()

    account = CybosKosdaqAccount()

    finalize_timer.start()
    bull_timer.start()
    app.exec()
    logger.exit_main_log()
