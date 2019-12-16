from morning.logging import logger
from morning.pipeline.converter import dt

class InMarketFilter:
    def __init__(self):
        self.next_elements = []

    def set_output(self, next_ele):
        self.next_elements.append(next_ele)

    def finalize(self):
        for next_ele in self.next_elements:
            next_ele.finalize()

    def received(self, datas):
        if len(self.next_elements) > 0:
            filtered_datas = []
            for data in datas:
                d = data['date']
                in_time =  (d.hour >= 9 and d.minute > 2) and (d.hour <=15 and d.minute < 20)
                if data['market_type'] == dt.MarketType.IN_MARKET:
                    filtered_datas.append(data)
                elif data['market_type'] == dt.MarketType.PRE_MARKET_EXP and in_time: # VI
                    filtered_datas.append(data)
            
            if len(filtered_datas):
                for n in self.next_elements:
                    n.received(filtered_datas)
