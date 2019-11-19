
from datetime import datetime


class MongoStockBaRealtime:
    def __init__(self, code, callback):
        self.code = code
        self.callback = callback

    
