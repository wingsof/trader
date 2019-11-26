from morning.pipeline.converter import dt


class StockDayTickConverter:
    def __init__(self):
        self.next_elements = None

    def set_output(self, next_ele):
        self.next_elements = next_ele

    def received(self, datas):
        if self.next_elements is not None:
            converted_datas = []
            for data in datas:
                converted_datas.append(dt.cybos_stock_day_tick_convert(data))
            self.next_elements.received(converted_datas)