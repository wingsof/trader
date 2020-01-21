from pymongo import MongoClient

import sys, signal
from PyQt5.QtCore import QCoreApplication, QTimer


count = 3

def hello():
    global count
    count -= 1
    print('timer')
    if count == 0:
        finalize_timer.stop()
        print('stop')


if __name__ == '__main__':
    app = QCoreApplication(sys.argv)
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    finalize_timer = QTimer()
    finalize_timer.setInterval(1000)
    finalize_timer.timeout.connect(hello)
    finalize_timer.start()
    app.exec()

"""
db = MongoClient('mongodb://192.168.0.22:27017')
with db:
    stock_db = db['stock']
    collections = stock_db.collection_names()
    for c in collections:
        if c.endswith('_M'):
            stock_db[c].drop()


    stock = MongoClient(db.HOME_MONGO_ADDRESS)['stock']
    remote_codes = []
    kospi_codes = list(stock['KOSPI_CODES'].find())
    kosdaq_codes = list(stock['KOSDAQ_CODES'].find())
    codes = []
    codes.extend(kospi_codes)
    codes.extend(kosdaq_codes)

    for code in codes:
        remote_codes.append(code['code'])
    
    for code in remote_codes:
        stock[code + '_D'].drop()
"""