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
        for i in range(13):
            d[str(i)] = self.obj.GetHeaderValue(i)
        d['date'] = datetime.now()
        self.filter_callback(self.sock, self.code, [d])


class _WorldRealtime:
    def __init__(self, code):
        self.obj = win32com.client.Dispatch("CpSysDib.WorldCur")
        self.code = code

    def subscribe(self, sock, filter_callback):
        handler = win32com.client.WithEvents(self.obj, _CpEvent)
        self.obj.SetInputValue(0, self.code)
        handler.set_params(self.obj, self.code, sock, filter_callback)
        self.obj.Subscribe()

    def unsubscribe(self):
        self.obj.Unsubscribe()


class WorldSubscribe:
    def __init__(self, sock, code):
        self.sock = sock
        self.world_realtime = _WorldRealtime(code)

    def start_subscribe(self, callback):
        self.world_realtime.subscribe(self.sock, callback)

    def stop_subscribe(self):
        self.world_realtime.unsubscribe()
