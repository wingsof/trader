import win32com.client
from datetime import datetime


class _CpEvent:
    def set_params(self, obj, code, filter_callback):
        self.obj = obj
        self.code = code
        self.filter_callback = filter_callback

    def OnReceived(self):
        d = {}
        for i in range(29):
            d[str(i)] = self.obj.GetHeaderValue(i)
        d['date'] = datetime.now()
        d['stream'] = 'CybosStockTick'
        d['target'] = self.code
        self.filter_callback([d])


class StockRealtime:
    def __init__(self, code):
        self.obj = win32com.client.Dispatch('DsCbo1.StockCur')
        self.code = code

    def subscribe(self, filter_callback):
        handler = win32com.client.WithEvents(self.obj, _CpEvent)
        self.obj.SetInputValue(0, self.code)
        handler.set_params(self.obj, self.code, filter_callback)
        self.obj.Subscribe()

    def unsubscribe(self):
        self.obj.Unsubscribe()


class CybosStockTick:
    def __init__(self):
        self.next_element = None
        self.stock_realtime = None

    def set_target(self, target):
        code = target
        if ':' in target:
            code = target.split(':')[1]
        self.target_code = code
        self.stock_realtime = StockRealtime(code)

    def set_output(self, next_ele):
        self.next_element = next_ele
        self.stock_realtime.subscribe(self.next_element.received)

    def add_child_streams(self, s):
        pass

    def finalize(self):
        pass

    def received(self, data):
        pass

    def have_clock(self):
        return False