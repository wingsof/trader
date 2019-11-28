from morning.logging import logger



class ProfitDecision:
    def __init__(self):
        self.queue = None
        
    def set_output(self):
        pass

    def set_environ(self, queue):
        self.queue = queue

    def finalize(self):
        pass

    def received(self, datas):
        if self.queue is None or len(datas) == 0:
            logger.warning(self.__class__.__name__, 'No queue error')
            return

        for d in datas:
            stream_name = d['stream']
            value = 0
            value = d['value']
            if 'price' in datas[-1]:
                value = d['price']
            elif 'profit' in datas[-1]:
                value = d['profit']
            
            target, date = datas[-1]['target'], datas[-1]['date']
            strategy = datas[-1]['name']
            self.queue.put_nowait({ 'target': target, 'date': date, 'stream': stream_name,
                                            'strategy': strategy, 'result': True, 'value': value})