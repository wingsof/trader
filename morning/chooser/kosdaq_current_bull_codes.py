
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # for cybos_api

import chooser
from datetime import datetime
from pymongo import MongoClient
from PyQt5.QtCore import QTimer, pyqtSlot
from cybos_api.cp7043 import Cp7043

class KosdaqCurrentBullCodes(chooser.Chooser):

    def __init__(self, is_repeat = False, from_datetime = datetime.now(), until_datetime = datetime.now(), repeat_msec = 0):
        super().__init__()
        self.is_repeat = is_repeat
        self.is_running = False
        self.current_codes = []
        self.timer = QTimer(self)
        
        if is_repeat:
            self.timer.setInterval(repeat_msec)
            self.timer.timeout.connect(self.repeater)
        else:
            db = MongoClient('mongodb://nnnlife.iptime.org:27017')['stock']
            self.current_codes.extend(list(db['KOSDAQ_BY_TRADED'].find({'date': {'$gte':from_datetime, '$lte': until_datetime}})))

    @pyqtSlot()
    def repeater(self):
        cp =  Cp7043()
        codes = []
        cp.request(codes)
        diff = set(codes).difference(self.current_codes)
        if len(set(codes).difference(self.current_codes)) > 0:
            self.current_codes.extend(diff)
            code_set = {}
            for c in diff:
                code_set.add('stock_code:kosdaq:' + c)
            self.code_changed.emit(code_set)

    def run(self):
        if self.is_running:
            print('KosdaqCurrentBullCodes is already running')
            return False

        if self.is_repeat:
            self.timer.start()
        else:
            if len(self.current_codes) == 0:
                print('KosdaqCurrentBullCodes no codes')
                return False
            self.fetch_codes_and_emit(self.current_codes)
        self.is_running = True
        return True

    def fetch_codes_and_emit(self, codes):
        code_set = set()
        for code in codes:
            code.pop('_id', None)
            code.pop('date', None)
            for c in code.values():
                code_set.add('stock_code:kosdaq:' + c)
        self.code_changed.emit(code_set)


if __name__ == '__main__':
    from PyQt5.QtCore import QCoreApplication, QTimer, QObject
    import sys
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    class CodeReceiver(QObject):
        def __init__(self):
            super().__init__()
            self.kosdaq = KosdaqCurrentBullCodes(is_repeat = False, from_datetime=datetime(2019, 11, 15, 8, 50, 0), until_datetime=datetime(2019, 11, 15, 9, 5, 0))
            self.kosdaq.code_changed.connect(self.get_codes)
            self.kosdaq.run()

        @pyqtSlot(set)
        def get_codes(self, codes):
            print(codes)

    class CybosReceiver(QObject):
        def __init__(self):
            self.kosdaq = KosdaqCurrentBullCodes(is_repeat = True, repeat_msec = 5)
            self.kosdaq.code_changed.connect(self.get_codes)
            self.kosdaq.run()

        @pyqtSlot(set)
        def get_codes(self, codes):
            print(codes)


    app = QCoreApplication(sys.argv)
    #r = CodeReceiver()
    cr = CybosReceiver()
    app.exec()