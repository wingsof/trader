import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest

from PyQt5.QtCore import QTimer
from morning.trader import Trader
from morning_main import morning_launcher

from datetime import datetime

def trading():
    test_count = 3
    while test_count > 0:
        tr = Trader(False)
        QTimer.singleShot(1500, tr.app.quit)
        tr.run()
        test_count -= 1

def test_trader_creation():
    morning_launcher.morning_launcher(True, trading)

if __name__ == '__main__':
    test_trader_creation()