import win32com.client
from datetime import datetime


class _CpEvent:
    def set_params(self, obj, code, filter_callback):
        self.code = code
        self.obj = obj
        self.filter_callback = filter_callback

    def OnReceived(self):
        d = {}
        for i in range(69):
            d[str(i)] = self.obj.GetHeaderValue(i)
        d['date'] = datetime.datetime.now()
        d['stream'] = 'CybosBidAskTick'
        d['target'] = self.code
        self.filter_callback([d])


class BidAskRealtime:
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
    def __init__(self):
        self.next_element = None
        self.bidask_realtime = None

    def set_target(self, target):
        code = target.split(':')[1]
        self.target_code = code
        self.bidask_realtime = BidAskRealtime(code)

    def set_output(self, next_ele):
        self.next_element = next_ele
        self.bidask_realtime.subscribe(self.next_element.received)

    def clock(self, _):
        pass

    def received(self, data):
        pass

    def have_clock(self):
        return False
