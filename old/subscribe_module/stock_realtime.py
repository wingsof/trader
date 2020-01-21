import win32com.client
from pymongo import MongoClient
import datetime
import sys
from PyQt5.QtCore import QCoreApplication, QTimer
import time

import connection
import stock_code
import time
import bidask_realtime
import stock_daily_insert
import db

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
    def set_params(self, code, client, db_conn):
        self.client = client
        self.db = db_conn.stock
        self.code = code

    def OnReceived(self):
        d = {}
        for i in range(8):
            d[str(i)] = self.client.GetHeaderValue(i)
        d['date'] = datetime.datetime.now()
        self.db[self.code].insert_one(d)


class KospiRealtime:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def subscribe(self):
        self.kospi = win32com.client.Dispatch("DsCbo1.StockIndexIS")
        handler = win32com.client.WithEvents(self.kospi, CpKospi)
        self.kospi.SetInputValue(0, 'U001')
        handler.set_params('U001', self.kospi, self.db_connection)
        self.kospi.Subscribe()

        self.kosdaq = win32com.client.Dispatch("DsCbo1.StockIndexIS")
        handler2 = win32com.client.WithEvents(self.kosdaq, CpKospi)
        self.kosdaq.SetInputValue(0, 'U201')
        handler2.set_params('U201', self.kosdaq, self.db_connection)
        self.kosdaq.Subscribe()

        self.kospi200 = win32com.client.Dispatch("DsCbo1.StockIndexIS")
        handler3 = win32com.client.WithEvents(self.kospi200, CpKospi)
        self.kospi200.SetInputValue(0, 'U180')
        handler3.set_params('U180', self.kospi200, self.db_connection)
        self.kospi200.Subscribe()

    def unsubscribe(self):
        self.kospi.Unsubscribe()
        self.kosdaq.Unsubscribe()
        self.kospi200.Unsubscribe()


class WorldSubscribe:
    def __init__(self):
        self.world_list = ['JP#NI225', '.DJI', '399102', '95079',
                            'CZ#399106', 'COMP', 'HK#HS', 'HSCE',
                            'GR#DAX', 'JP#NI225', 'SHANG', 'SPX', 'EDNH', 'SOX', 'ENXH']

        self.client = MongoClient(db.HOME_MONGO_ADDRESS)
        self.is_running = False

    def start(self):
        print('Start World Subscribe', flush=True)
        self.is_running = True
 
        self.kospi_realtime =  KospiRealtime(self.client)
        self.world_realtime = []
        for c in self.world_list:
            self.world_realtime.append(StockWorldRealtime(c, self.client))

        self.kospi_realtime.subscribe()

        for w in self.world_realtime:
            w.subscribe()

    def stop(self):
        print('Stop World Subscribe', flush=True)
        self.is_running = False

        self.kospi_realtime.unsubscribe()

        for w in self.world_realtime:
            w.unsubscribe()


class Main:
    def __init__(self):
        self.is_running = False
        self.world = WorldSubscribe()
        self.bidask = bidask_realtime.BidAsk()
        self.timer = QTimer()
        self.timer.timeout.connect(self.time_check)
        self.timer.start(1000)
        self.last_loop_time = [0, 0]

    def network_check(self):
        conn = connection.Connection()
        if not conn.is_connected():
            print('ALERT: Network not connected', flush=True)
            # do something to alert me

    def _loop_print(self):
        t = datetime.datetime.now()
        if self.last_loop_time[0] != t.hour or self.last_loop_time[1] != t.minute:
            print('Main Loop', t, flush=True)
            self.last_loop_time[0] = t.hour
            self.last_loop_time[1] = t.minute
            self.network_check()

    def time_check(self):
        n = datetime.datetime.now()
        self._loop_print()

        if n.hour > 7 and n.hour < 18 and not self.is_running and n.weekday() < 5:
            self.world.start()
            self.bidask.start()
            self.is_running = True
        else:
            if self.is_running and n.hour >= 18:
                self.is_running = False
                self.world.stop()
                self.bidask.stop()
                #print('INSERT DAILY DATA', flush=True)
                #stock_daily_insert.daily_insert_data()


if __name__ == '__main__':
    time.sleep(60*3)

    conn = connection.Connection()
    while not conn.is_connected():
        time.sleep(5)
    
    print("World Realtime Run", flush=True)

    app = QCoreApplication(sys.argv)
    m = Main()
    app.exec()
    
