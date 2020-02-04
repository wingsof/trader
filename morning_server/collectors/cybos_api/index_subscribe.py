import win32com.client
from datetime import datetime


class _CpEvent:
    def set_params(self, obj, code, sock, filter_callback):
        self.obj = obj
        self.code = code
        self.sock = sock
        self.filter_callback = filter_callback

    def OnReceived(self):
        d = {}
        for i in range(8):
            d[str(i)] = self.client.GetHeaderValue(i)
        d['date'] = datetime.now()
        self.filter_callback(self.sock, self.code, [d])


class _IndexRealtime:
    def __init__(self, code):
        self.obj = win32com.client.Dispatch("DsCbo1.StockIndexIS")
        self.code = code

    def subscribe(self, sock, filter_callback):
        handler = win32com.client.WithEvents(self.obj, _CpEvent)
        self.obj.SetInputValue(0, self.code)
        handler.set_params(self.obj, self.code, sock, filter_callback)
        self.obj.Subscribe()

    def unsubscribe(self):
        self.obj.Unsubscribe()


class IndexSubscribe:
    def __init__(self, sock, code):
        self.sock = sock
        self.index_realtime = _IndexRealtime(code)

    def start_subscribe(self, callback):
        self.index_realtime.subscribe(self.sock, callback)

    def stop_subscribe(self):
        self.bidask_realtime.unsubscribe()
