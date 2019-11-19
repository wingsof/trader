from morning.streams.data_converter.data_converter import DataConverter
from morning import tdef


class StockTickConverter(DataConverter):
    def __init__(self):
        pass

    def vendor(self):
        return tdef.vendors[tdef.Vendor.CYBOS]

    def accept_in(self):
        return [tdef.data_format[tdef.DataFormat.STOCK_TICK_REALTIME]]

    def output_format(self):
        return tdef.data_format[tdef.DataFormat.STOCK_TICK_REALTIME]
