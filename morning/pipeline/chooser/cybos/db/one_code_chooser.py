from datetime import datetime

from morning.pipeline.chooser.chooser import Chooser

import time

class DatabaseOneCodeChooser(Chooser):
    def __init__(self, code, from_datetime = datetime.now(), until_datetime = datetime.now()):
        super().__init__()
        self.code = code

    def start(self):
        self.selection_changed.emit(set(['cybos:' + self.code]))
