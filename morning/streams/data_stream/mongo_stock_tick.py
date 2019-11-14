
from datetime import datetime




class MongoStockBaRealtime:
    def __init__(self, code, callback):
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
