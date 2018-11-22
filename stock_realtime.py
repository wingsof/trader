import win32com.client
from pymongo import MongoClient
import datetime
import sys


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
        print("kospi200 received")
        d = {}
        for i in range(8):
            d[str(i)] = self.client.GetHeaderValue(i)
        d['date'] = datetime.datetime.now()
        self.db.kospi.insert_one(d)


class KospiRealtime:
    def __init__(self, db_connection):
        self.db_connection = db_connection
        self.code = '00800'

    def subscribe(self):
        self.obj = win32com.client.Dispatch("DsCbo1.FutureIndexI")
        handler = win32com.client.WithEvents(self.obj, CpKospi)
        self.obj.SetInputValue(0, self.code)
        handler.set_params(self.obj, self.db_connection)
        self.obj.Subscribe()

    def unsubscribe(self):
        self.obj.Unsubscribe()


if __name__ == '__main__':
    print("Run")
    from PyQt5.QtCore import QCoreApplication
    import connection
    import stock_code

    conn = connection.Connection()
    client = MongoClient('mongodb://192.168.0.22:27017')

    if conn.is_connected():
        app = QCoreApplication(sys.argv)
        code_list = stock_code.StockCode.get_kospi200_list()
        stock_realtime = []
        for code in code_list:
            st = StockRealtime(code, client)
            stock_realtime.append(st)
            st.subscribe()

        kospi_realtime = KospiRealtime(client)
        kospi_realtime.subscribe()

        world_list = ['JP#NI225', '.DJI', '399102', '95079',
                      'CZ#399106', 'COMP', 'HK#HS', 'HSCE',
                      'GR#DAX', 'JP#NI225', 'SHANG', 'SPX', 'EDNH', 'SOX', 'ENXH']
        world_realtme = []
        for code in world_list:
            swr = StockWorldRealtime(code, client)
            world_realtme.append(swr)
            swr.subscribe()
        print("Subscribe started")

        app.exec()
    else:
        print("Not Connected")