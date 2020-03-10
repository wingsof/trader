import win32com.client
from datetime import datetime


class _CpEvent:
    def set_params(self, obj, code, callback):
        self.obj = obj
        self.code = code
        self.callback = callback

    def OnReceived(self):
        d = {}
        for i in range(69):
            d[str(i)] = self.obj.GetHeaderValue(i)
        d['date'] = datetime.now()
        self.callback(self.code, [d])


class _BidAskRealtime:
    def __init__(self, code, callback):
        self.obj = win32com.client.gencache.EnsureDispatch("DsCbo1.StockJpBid")
        self.handler = win32com.client.WithEvents(self.obj, _CpEvent)
        self.obj.SetInputValue(0, code)
        self.handler.set_params(self.obj, code, callback)

    def subscribe(self):
        self.obj.Subscribe()

    def unsubscribe(self):
        self.obj.Unsubscribe()


class BidAskSubscribe:
    def __init__(self, code, callback):
        self.started = False
        self.code = code
        self.bidask_realtime = _BidAskRealtime(code, callback)

    def start_subscribe(self):
        if not self.started:
            self.bidask_realtime.subscribe()
            self.started = True
            print('START subscribe bidask ', self.code)

    def stop_subscribe(self):
        if self.started:
            self.bidask_realtime.unsubscribe()
            self.started = False
            print('STOP subscribe bidask ', self.code)
