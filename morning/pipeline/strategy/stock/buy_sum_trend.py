from morning.logging import logger


class BuySumTrend:
    def __init__(self):
        self.next_elements = None
        self.last_result = False

    def set_output(self, next_ele):
        self.next_elements = next_ele

    def received(self, datas):
        if self.next_elements is not None:
            result = True
            for d in datas:
                if d['cum_buy_volume'] <= d['cum_sell_volume']:
                   result = False 
            
            if self.last_result ^ result:
                logger.print({'name':self.__class__.__name__, 'type': 'Bool', 'value': str(result)}, d['time_with_sec'])
                self.next_elements.received([{'name':self.__class__.__name__, 
                                            'target': datas[-1]['target'],
                                            'stream': datas[-1]['stream'], 
                                            'date': datas[-1]['date'],
                                            'value': result}])
                self.last_result = result
