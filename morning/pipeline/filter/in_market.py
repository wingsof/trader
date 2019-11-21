from morning.logging import logger
from morning.pipeline.converter import dt

class InMarketFilter:
    def __init__(self):
        self.next_elements = None

    def set_output(self, next_ele):
        self.next_elements = next_ele

    def received(self, datas):
        if self.next_elements is not None:
            filtered_datas = []
            for data in datas:
                if data['market_type'] == dt.MarketType.IN_MARKET:
                    filtered_datas.append(data)
            
            if len(filtered_datas):
                self.next_elements.received(filtered_datas)
