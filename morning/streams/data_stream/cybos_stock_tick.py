import win32com.client
from datetime import datetime

from morning.streams.data_stream.data_stream import DataStream

class _CpEvent:
    def set_params(self, obj, code, callback):
        self.obj = obj
        self.code = code
        self.callback = callback

    def OnReceived(self):
        d = {}
        for i in range(29):
            d[str(i)] = self.obj.GetHeaderValue(i)
        d['date'] = datetime.now()
        self.callback(d)


class CybosStockTick(DataStream):

    def __init__(self):
        super().__init__('cybos_stock_tick', True)
        self.obj = None
        self.code = ''
        self.callback = None

    def set_target(self, code, callback):
        self.obj = win32com.client.Dispatch('DsCbo1.StockCur')
        self.code = code
        self.callback = callback

    def subscribe(self):
        handler = win32com.client.WithEvents(self.obj, _CpEvent)
        self.obj.SetInputValue(0, self.code)
        handler.set_params(self.obj, self.code, self.callback)
        self.obj.Subscribe()

    def unsubscribe(self):
        self.obj.Unsubscribe()
