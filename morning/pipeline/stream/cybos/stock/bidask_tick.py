import win32com.client
from datetime import datetime
from morning.pipeline.converter.cybos.stock.bidask import StockBidAskTickConverter

class _CpEvent:
    def set_params(self, code, obj, filter_callback):
        self.code = code
        self.obj = obj
        self.filter_callback = filter_callback

    def OnReceived(self):
        d = {}
        for i in range(69):
            d[str(i)] = self.obj.GetHeaderValue(i)
        d['date'] = datetime.now()
        d['stream'] = 'CybosBidAskTick'
        d['target'] = self.code
        self.filter_callback([d])


class _BidAskRealtime:
    def __init__(self, code):
        self.obj = win32com.client.Dispatch("DsCbo1.StockJpBid")
        self.code = code

    def subscribe(self, filter_callback):
        handler = win32com.client.WithEvents(self.obj, _CpEvent)
        self.obj.SetInputValue(0, self.code)
        handler.set_params(self.code, self.obj, filter_callback)
        self.obj.Subscribe()

    def unsubscribe(self):
        self.obj.Unsubscribe()


class CybosBidAskTick:
    def __init__(self, use_converter=True):
        self.next_element = None
        self.bidask_realtime = None
        self.use_converter = use_converter
        if use_converter:
            self.bidask_converter = StockBidAskTickConverter()
            self.bidask_converter.set_output(self)

    def set_target(self, target):
        code = target
        if ':' in target:
            code = target.split(':')[1]
        self.target_code = code
        self.bidask_realtime = _BidAskRealtime(code)
        if self.use_converter:
            self.bidask_realtime.subscribe(self.bidask_converter.received)

    def set_output(self, next_ele):
        self.next_element = next_ele

    def received(self, data):
        if self.next_element:
            self.next_element.received(data)

    def clock(self, _):
        pass

    def have_clock(self):
        return False
