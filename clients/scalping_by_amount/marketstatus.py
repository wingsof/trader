from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))

from morning.pipeline.converter import dt
from configs import time_info
from datetime import datetime


class MarketStatus:
    PRE_MARKET = 0
    IN_MARKET = 1
    VI = 2
    CLOSE = 3

    def __init__(self):
        self.status = MarketStatus.PRE_MARKET

    def set_tick_data(self, data):
        prev_status = self.status

        market_type = tick_data['market_type']
        if self.status == MarketStatus.PRE_MARKET and market_type == dt.MarketType.IN_MARKET:
            self.status = MarketStatus.IN_MARKET
        elif self.status == MarketStatus.IN_MARKET and market_type == dt.MarketType.PRE_MARKET_EXP:
            now = datetime.now()
            open_time = now.replace(hour=time_info.MARKET_OPEN_TIME['hour'], minute=time_info.MARKET_OPEN_TIME['minute'])
            close_time = now.replace(hour=time_info.MARKET_CLOSE_TIME['hour'], minute=time_info.MARKET_CLOSE_TIME['minute'])
            if open_time <= now <= close_time:
                self.status = MarketStatus.VI
            else:
                self.status = MarketStatus.CLOSE
        elif self.status == MarketStatus.STATUS_VI and market_type == dt.MarketType.IN_MARKET:
            self.status = MarketStatus.IN_MARKET

        return prev_status != self.status

    def get_market_status(self):
        return self.status

    def is_in_market(self):
        return self.status == MarketStatus.IN_MARKET
