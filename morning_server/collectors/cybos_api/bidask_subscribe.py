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
        for i in range(69):
            d[str(i)] = self.obj.GetHeaderValue(i)
        d['code'] = self.code
        self.filter_callback(self.sock, [d])


class _BidAskRealtime:
    def __init__(self, code):
        self.obj = win32com.client.Dispatch("DsCbo1.StockJpBid")
        self.code = code

    def subscribe(self, sock, filter_callback):
        handler = win32com.client.WithEvents(self.obj, _CpEvent)
        self.obj.SetInputValue(0, self.code)
        handler.set_params(self.obj, self.code, sock, filter_callback)
        self.obj.Subscribe()

    def unsubscribe(self):
        self.obj.Unsubscribe()


class BidAskSubscribe:
    def __init__(self, sock, code):
        self.sock = sock
        self.bidask_realtime = _BidAskRealtime(code)

    def start_subscribe(self, callback):
        self.bidask_realtime.subscribe(self.sock, callback)

    def stop_subscribe(self):
        self.bidask_realtime.unsubscribe()
