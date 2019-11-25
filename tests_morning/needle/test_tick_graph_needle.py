import pytest
from morning.needle.tick_graph_needle import TickGraphNeedle
from datetime import date, datetime

def test_tick_graph_needle():
    class TestStg:
        def __init__(self):
            self.tgn = None

        def add_graph(self, tgn):
            self.tgn = tgn

        def send_received(self, d):
            self.tgn.received(d)

    stg = TickGraphNeedle()
    stg.filter_codes(['A000001'])
    test_tsg = TestStg()
    stg.tick_connect(test_tsg)
    test_data1 = [{'date': datetime(2019, 11, 22, 9, 0, 10), 'code': 'A000001', 'current_price': 100, 'volume': 10}, 
                  {'date': datetime(2019, 11, 22, 9, 0, 20), 'code': 'A000001', 'current_price': 200, 'volume': 20},
                  {'date': datetime(2019, 11, 22, 9, 1, 10), 'code': 'A000001', 'current_price': 300, 'volume': 30},
                  {'date': datetime(2019, 11, 22, 9, 3, 20), 'code': 'A000001', 'current_price': 400, 'volume': 40},
                  {'date': datetime(2019, 11, 22, 9, 3, 40), 'code': 'A000001', 'current_price': 500, 'volume': 50}]
    
    stg.filter_date(date(2019, 11, 22))
    for t in test_data1:
        print('date' in t)
        test_tsg.send_received([t])
    assert len(stg.df) == 5
    published = stg.out_min_graph()
    assert published[0] == 'A000001'