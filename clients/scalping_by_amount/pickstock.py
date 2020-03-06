from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))

import gevent

from clients.common import morning_client
from morning_server import message
from clients.scalping_by_amount import price_info
from morning_server import stock_api


class PickStock:
    def __init__(self):
        pass

    def is_satisfy_slot(self, p, today_open, profit, is_kospi, yclose):
        slots = price_info.create_slots(yclose, p, today_open, is_kospi)
        slot_count = len(price_info.upper_available_empty_slots(slots))
        if slot_count > 10:
            return True

        return False

    def pick_one(self, candidates):
        by_amount = sorted(candidates, key=lambda x: x['amount'])
        # already filtered : profit > 0, yesterday_close != 0
        for ba in by_amount[:10]:
            c = ba['current_price']
            current_profit_by_yesterday = (c - ba['yesterday_close']) / ba['yesterday_close'] * 100
            current_profit_by_open = (c - ba['today_open']) / ba['today_open'] * 100
            #if current_profit_by_yesterday > 20.:
            #    continue
            if self.is_satisfy_slot(c, ba['today_open'], current_profit_by_open, ba['is_kospi'], ba['yesterday_close']):
                return ba
        return None
