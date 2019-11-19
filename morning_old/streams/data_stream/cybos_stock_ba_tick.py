import win32com.client
from datetime import datetime
from morning.streams.data_stream.data_stream import DataStream
from morning import tdef


class _BaEvent:
    def set_params(self, obj, code, callback):
        self.code = code
        self.obj = obj
        self.callback = callback

    def OnReceived(self):
        d = {}
        for i in range(69):
            d[str(i)] = self.obj.GetHeaderValue(i)
        d['date'] = datetime.datetime.now()
        self.callback(d)


class CybosStockBaTick(DataStream):
    def __init__(self):
        super().__init__('cybos_stock_ba_tick', True)
        self.obj = None
        self.code = ''
        self.callback = None
        
    def set_target(self, code, callback):
        self.obj = win32com.client.Dispatch("DsCbo1.StockJpBid")
        self.code = code
        self.callback = callback

    def subscribe(self):
        handler = win32com.client.WithEvents(self.obj, _BaEvent)
        self.obj.SetInputValue(0, self.code)
        handler.set_params(self.code, self.obj, self.callback)
        self.obj.Subscribe()

    def unsubscribe(self):
        self.obj.Unsubscribe()

    def vendor(self):
        return tdef.vendors[tdef.Vendor.CYBOS]

    def accept_in(self):
        return [tdef.data_format[tdef.DataFormat.STOCK_CODE]]

    def output_format(self):
        return tdef.data_format[tdef.DataFormat.STOCK_BIDASK_REALTIME]

