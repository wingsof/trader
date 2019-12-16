import pytest
from datetime import datetime
from morning.pipeline.strategy.stock.realtime_minute_suppressed import RealtimeMinuteSuppressed


class Receiver:
    last_min_tick = None

    def received(self, datas):
        assert len(datas) == 1
        self.last_min_tick = datas[0]

def test_time_gap():
    rcv = Receiver()
    rms = RealtimeMinuteSuppressed()
    rms.ms = rcv

    sample1 = {
            'date': datetime(2019, 2, 1, 9, 1, 1),
            'cum_buy_volume': 1,
            'cum_sell_volume': 1,
            'current_price': 100,
            'stream': 'Receiver',
            'target': 'A000001'
    }
    sample2 = {
            'date': datetime(2019, 2, 1, 9, 3, 1),
            'cum_buy_volume': 1,
            'cum_sell_volume': 1,
            'current_price': 150,
            'stream': 'Receiver',
            'target': 'A000001'
    }

    rms.received([sample1])
    assert rcv.last_min_tick == None
    rms.received([sample2])
    assert rcv.last_min_tick is not None
    assert rcv.last_min_tick['date'] == datetime(2019, 2, 1, 9, 1)
    assert rcv.last_min_tick['close_price'] == 150 # intended
