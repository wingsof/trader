from datetime import datetime
from PyQt5.QtCore import QObject, QCoreApplication, QTimer, pyqtSlot

from morning.pipeline.chooser.cybos.db.kosdaq_bull_chooser import KosdaqBullChooser

import pytest

def test_get_bull_codes():
    class Receiver(QObject):
        def __init__(self):
            super().__init__()
            self.targets = []

        @pyqtSlot(set)
        def received(self, targets):
            self.targets.extend(list(targets))

    app = QCoreApplication([])
    recv = Receiver()
    kbc = KosdaqBullChooser(from_datetime=datetime(2019,11,19,0,0,0), until_datetime=datetime(2019,11,20,0,0,0))
    kbc.selection_changed.connect(recv.received)
    kbc.start()
    QTimer.singleShot(1000, app.exit)
    app.exec() 
    assert len(recv.targets)
    for target in recv.targets:
        assert target.startswith('cybos:A')
