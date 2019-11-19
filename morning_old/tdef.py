
from enum import Enum

class Vendor(Enum):
    CYBOS = 1

vendors = {}
vendors[Vendor.CYBOS] = 'cybos'

class DataFormat(Enum):
    STOCK_CODE = 1
    STOCK_TICK_REALTIME = 2
    STOCK_BIDASK_REALTIME = 3
    STOCK_TICK_BACKTEST = 4

data_format[DataFormat.STOCK_CODE] = 'stock_code'
data_format[DataFormat.STOCK_TICK_REALTIME] = 'stock_tick_realtime'
data_format[DataFormat.STOCK_BIDASK_REALTIME] = 'stock_bidask_realtime'
data_format[DataFormat.STOCK_TICK_BACKTEST] = 'stock_tick_backtest'

