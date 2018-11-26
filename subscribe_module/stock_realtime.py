import win32com.client
from pymongo import MongoClient
import datetime
import sys
from PyQt5.QtCore import QCoreApplication, QTimer

import connection
import stock_code
import time


class CpEvent:
    def set_params(self, code, client, db_conn):
        self.code = code
        self.client = client
        self.db = db_conn.stock
        self.db[self.code]

    def OnReceived(self):
        d = {}
        for i in range(29):
            d[str(i)] = self.client.GetHeaderValue(i)
        d['date'] = datetime.datetime.now()
        self.db[self.code].insert_one(d)


class StockRealtime:
    def __init__(self, code, db_connection):
        self.db_connection = db_connection
        self.code = code

    def subscribe(self):
        self.obj = win32com.client.Dispatch("DsCbo1.StockCur")
        handler = win32com.client.WithEvents(self.obj, CpEvent)
        self.obj.SetInputValue(0, self.code)
        handler.set_params(self.code, self.obj, self.db_connection)
        self.obj.Subscribe()

    def unsubscribe(self):
        self.obj.Unsubscribe()


class CpWorldCur:
    def set_params(self, client, db_conn):
        self.client = client
        self.db = db_conn.stock
        self.db.world_cur

    def OnReceived(self):
        d = {}
        for i in range(13):
            d[str(i)] = self.client.GetHeaderValue(i)
        d['date'] = datetime.datetime.now()
        self.db.world_cur.insert_one(d)


class StockWorldRealtime:
    def __init__(self, code, db_connection):
        self.db_connection = db_connection
        self.code = code

    def subscribe(self):
        self.obj = win32com.client.Dispatch("CpSysDib.WorldCur")
        handler = win32com.client.WithEvents(self.obj, CpWorldCur)
        self.obj.SetInputValue(0, self.code)
        handler.set_params(self.obj, self.db_connection)
        self.obj.Subscribe()

    def unsubscribe(self):
        self.obj.Unsubscribe()


class CpKospi:
    def set_params(self, client, db_conn):
        self.client = client
        self.db = db_conn.stock
        self.db.kospi

    def OnReceived(self):
        d = {}
        for i in range(8):
            d[str(i)] = self.client.GetHeaderValue(i)
        d['date'] = datetime.datetime.now()
        self.db.kospi.insert_one(d)


class KospiRealtime:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def subscribe(self):
        self.obj = win32com.client.Dispatch("DsCbo1.StockIndexIS")
        handler = win32com.client.WithEvents(self.obj, CpKospi)
        self.obj.SetInputValue(0, 'U001')
        handler.set_params(self.obj, self.db_connection)
        self.obj.Subscribe()

        self.kosdaq = win32com.client.Dispatch("DsCbo1.StockIndexIS")
        handler2 = win32com.client.WithEvents(self.obj, CpKospi)
        self.kosdaq.SetInputValue(0, 'U201')
        handler2.set_params(self.obj, self.db_connection)
        self.kosdaq.Subscribe()

    def unsubscribe(self):
        self.obj.Unsubscribe()
        self.kosdaq.Unsubscribe()


class Main:
    def __init__(self):
        self.world_list = ['JP#NI225', '.DJI', '399102', '95079',
                            'CZ#399106', 'COMP', 'HK#HS', 'HSCE',
                            'GR#DAX', 'JP#NI225', 'SHANG', 'SPX', 'EDNH', 'SOX', 'ENXH']
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

        self.kospi_realtime =  KospiRealtime(self.client)
        self.world_realtime = []
        for c in self.world_list:
            self.world_realtime.append(StockWorldRealtime(c, self.client))

        for s in self.kospi_stocks_realtime:
            s.subscribe()

        self.kospi_realtime.subscribe()

        for w in self.world_realtime:
            w.subscribe()

    def stop(self):
        print('Stop Subscribe')
        self.is_running = False
        for s in self.kospi_stocks_realtime:
            s.unsubscribe()

        self.kospi_realtime.unsubscribe()

        for w in self.world_realtime:
            w.unsubscribe()


if __name__ == '__main__':
    conn = connection.Connection()
    while not conn.is_connected():
        time.sleep(5)
    
    print("Realtime Run")

    app = QCoreApplication(sys.argv)
    m = Main()
    app.exec()
    