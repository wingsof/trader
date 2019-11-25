import pytest
from datetime import datetime, date

from morning.needle.tick_excel_needle import TickExcelNeedle


def test_tick_excel_needle():
    class TestStg:
        def __init__(self):
            self.tgn = None

        def add_graph(self, tgn):
            self.tgn = tgn

        def send_received(self, d):
            self.tgn.received(d)

    ten = TickExcelNeedle()
    ten.filter_codes(['A000001'])
    test_tsg = TestStg()
    ten.tick_connect(test_tsg)
    test_data1 = [{'date': datetime(2019, 11, 22, 9, 0, 10), 'code': 'A000001', 'current_price': 100, 'volume': 10}, 
                  {'date': datetime(2019, 11, 22, 9, 0, 20), 'code': 'A000001', 'current_price': 200, 'volume': 20},
                  {'date': datetime(2019, 11, 22, 9, 1, 10), 'code': 'A000001', 'current_price': 300, 'volume': 30},
                  {'date': datetime(2019, 11, 22, 9, 3, 20), 'code': 'A000001', 'current_price': 400, 'volume': 40},
                  {'date': datetime(2019, 11, 22, 9, 3, 40), 'code': 'A000001', 'current_price': 500, 'volume': 50}]
    
    ten.filter_date(date(2019, 11, 22))
    for t in test_data1:
        print('date' in t)
        test_tsg.send_received([t])
    assert len(ten.df) == 5
    ten.process()
