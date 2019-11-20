from datetime import datetime

from morning.pipeline.chooser.chooser import Chooser

import time

class MockSamsungChooser(Chooser):
    def __init__(self, from_datetime = datetime.now(), until_datetime = datetime.now()):
        super().__init__()

    def start(self):
        self.selection_changed.emit(set(['A005930']))