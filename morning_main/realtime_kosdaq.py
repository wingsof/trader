import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime

from morning.trader import Trader
from morning.trading_tunnel import TradingTunnel
from morning_main import morning_launcher

from morning.account.cybos_kosdaq_account import CybosKosdaqAccount
from morning.pipeline.chooser.cybos.db.kosdaq_search_bull_chooser import KosdaqSearchBullChooser
from morning.pipeline.converter.cybos.stock.tick import StockTickConverter
from morning.pipeline.filter.in_market import InMarketFilter
from morning.pipeline.filter.drop_data import DropDataFilter
from morning.pipeline.decision.bool_and_decision import BoolAndDecision
from morning.pipeline.strategy.stock.realtime_minute_suppressed import RealtimeMinuteSuppressed

from morning.pipeline.stream.cybos.stock.tick import CybosStockTick

def trading():
    ksbc = KosdaqSearchBullChooser(datetime.now().date(), False) # not use database to search codes
    account = CybosKosdaqAccount()

    trader = Trader(True)
    tunnel = TradingTunnel(trader)

    tunnel.set_chooser(ksbc)

    pipeline = {'name': 'kosdaq_bull',
                'stream': CybosStockTick(),
                'converter': StockTickConverter(),
                'filter': [InMarketFilter(), DropDataFilter(1)],
                'strategy': [RealtimeMinuteSuppressed()],
                'decision': BoolAndDecision(1, 2)} # trade count = 2

    tunnel.add_pipeline(pipeline)
    trader.add_tunnel(tunnel)
    trader.set_account(account)

    #for code in ksbc.codes:
    #    account.set_bidask_monitoring(code)
    trader.run()


if __name__ == '__main__':
    # TODO block interrupt
    morning_launcher.morning_launcher(True, trading)

    