import pytest

from morning.pipeline.strategy.stock.yday_close_today_start import YdayCloseTodayStart
from datetime import datetime


def test_yday_close_today_start():
    class Receiver:
        def __init__(self):
            self.ok = False

        def received(self, datas):
            self.ok = True

    ycts = YdayCloseTodayStart(False)
    rcv = Receiver()
    ycts.set_output(rcv)

    test_data = [{'highest_price': 1000, 'start_price': 900, 'close_price': 900, 'target':'', 'stream':'', 'date': datetime.now()},
        {'highest_price': 1050, 'start_price': 950, 'close_price': 1000, 'target':'', 'stream':'', 'date': datetime.now()}]
    ycts.received(test_data)
    assert rcv.ok

    test_data = [{'highest_price': 1000, 'start_price': 900, 'close_price': 900, 'target':'', 'stream':'', 'date': datetime.now()},
        {'highest_price': 1050, 'start_price': 850, 'close_price': 1000, 'target':'', 'stream':'', 'date': datetime.now()}]
    ycts = YdayCloseTodayStart(True)
    rcv = Receiver()
    ycts.set_output(rcv)

    ycts.received(test_data)

    assert rcv.ok
