import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import connection
import stock_code
import time
import queue
import sys
import win32com.client
from datetime import datetime
from pymongo import MongoClient
import bidask_realtime
import stock_current_realtime

from multiprocessing import Process, Queue
from PyQt5.QtCore import QCoreApplication, QTimer

from morning.back_data.fetch_stock_data import get_day_period_data
from morning.back_data import holidays

class ShortCollector:
    def __init__(self, codes):
        self.current_subscribe_codes = []
        self.last_loop_time = [0, 0]
        self.realtime_subscribers = []
        self.client = MongoClient('mongodb://192.168.0.22:27017')

        for code in codes:
            bidask = bidask_realtime.StockRealtime(code, self.client)
            stock_current = stock_current_realtime.StockRealtime(code, self.client)
            self.realtime_subscribers.append(bidask)
            self.realtime_subscribers.append(stock_current)
            bidask.subscribe()
            stock_current.subscribe()


if __name__ == '__main__':
    time.sleep(60*3)
    today = datetime.now().date()
    yesterday = holidays.get_yesterday(today)
    conn = connection.Connection()
    while not conn.is_connected():
        time.sleep(5)
    
    codes = stock_code.StockCode.get_kosdaq_code_list()
    datas = []
    for code in codes:
        data = get_day_period_data(code, yesterday, yesterday)
        if len(data) > 0:
            data[0]['code'] = code
            datas.append(data[0])

    datas = sorted(datas, key=lambda i: i['7'], reverse=True)
    codes = [d['code'] for d in datas]
    codes = codes[:80]
    print("Short Strategy", flush=True)

    app = QCoreApplication(sys.argv)
    sc = ShortCollector(codes)
    app.exec()
