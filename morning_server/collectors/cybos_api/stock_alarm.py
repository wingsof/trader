import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..' + os.sep + '..')))


import win32com.client
import gevent

from morning_server.collectors.cybos_api import connection
from utils import rlogger


class _CpEvent:
    def set_params(self, obj, sock, filter_callback):
        self.obj = obj
        self.sock = sock
        self.filter_callback = filter_callback

    def OnReceived(self):
        d = {}
        for i in range(10):
            d[str(i)] = self.obj.GetHeaderValue(i)
        d['date'] = datetime.now()
        self.filter_callback(self.sock, [d])


class _AlarmRealtime:
    def __init__(self):
        self.obj = win32com.client.Dispatch("CpSysDib.CpSvr9619S")

    def subscribe(self, sock, filter_callback):
        handler = win32com.client.WithEvents(self.obj, _CpEvent)
        handler.set_params(self.obj, sock, filter_callback)
        self.obj.Subscribe()

    def unsubscribe(self):
        self.obj.Unsubscribe()


class StockAlarm:
    def __init__(self, sock):
        self.sock = sock
        self.alarm_realtime = _AlarmRealtime()

    def start_subscribe(self, callback):
        self.alarm_realtime.subscribe(self.sock, callback)

    def stop_subscribe(self):
        self.bidask_realtime.unsubscribe()
