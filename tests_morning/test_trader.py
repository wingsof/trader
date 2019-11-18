from PyQt5.QtCore import QTimer, pyqtSlot


from morning.trader import Trader
from morning.streams.data_stream.cybos_stock_tick import CybosStockTick
from morning.streams.data_stream.cybos_stock_ba_tick import CybosStockBaTick
from morning.chooser.chooser import Chooser

import pytest


def test_trader():
    class Children(Chooser):
        def __init__(self):
            super().__init__() 

        @pyqtSlot()
        def run(self):
            print('test timer run')
            QTimer.singleShot(1000, self.send_stock_code)

        @pyqtSlot()
        def send_stock_code(self):
            self.code_changed.emit({'stock_code:kosdaq:A000001',})


    trader = Trader(True)
    trader.set_stream_pipeline(CybosStockTick(), CybosStockBaTick())

    trader.set_chooser(Children())
    QTimer.singleShot(5000, trader.app.quit)
    trader.run()
    print(trader.trade_launcher.targets)
    assert 0 == 1

    
