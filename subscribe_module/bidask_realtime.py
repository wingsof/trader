import win32com.client
from pymongo import MongoClient
import datetime
import sys
import time
from PyQt5.QtCore import QCoreApplication, QTimer

import connection
import stock_code



class CpEvent:
    def set_params(self, code, client, db_conn):
        self.code = code
        self.client = client
        self.db = db_conn.stock
        self.db[self.code + '_BA']

    def OnReceived(self):
        d = {}
        for i in range(69):
            d[str(i)] = self.client.GetHeaderValue(i)
        d['date'] = datetime.datetime.now()
        self.db[self.code + '_BA'].insert_one(d)


class StockRealtime:
    def __init__(self, code, db_connection):
        self.db_connection = db_connection
        self.code = code

    def subscribe(self):
        self.obj = win32com.client.Dispatch("DsCbo1.StockJpBid")
        handler = win32com.client.WithEvents(self.obj, CpEvent)
        self.obj.SetInputValue(0, self.code)
        handler.set_params(self.code, self.obj, self.db_connection)
        self.obj.Subscribe()

    def unsubscribe(self):
        self.obj.Unsubscribe()


class Main:
    def __init__(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.time_check)
        self.client = MongoClient('mongodb://192.168.0.22:27017')
        self.is_running = False
        self.timer.start(1000)

    def time_check(self):
        n = datetime.datetime.now()
        if n.hour > 7 and n.hour < 17 and not self.is_running and n.weekday() < 5:
            self.start()
        else:
            if self.is_running and n.hour >= 17:
                self.stop()

    def start(self):
        print('Start Subscribe')
        self.is_running = True
        code_list = stock_code.StockCode.get_kospi200_list()
        self.kospi_stocks_realtime = []
        for c in code_list:
            self.kospi_stocks_realtime.append(StockRealtime(c, self.client))

        for s in self.kospi_stocks_realtime:
            s.subscribe()


    def stop(self):
        print('Stop Subscribe')
        self.is_running = False
        for s in self.kospi_stocks_realtime:
            s.unsubscribe()


if __name__ == '__main__':
    print("Run")
    conn = connection.Connection()

    while not conn.is_connected():
        time.sleep(5)

    print("BID ASK Run")

    app = QCoreApplication(sys.argv)
    m = Main()
    app.exec()
