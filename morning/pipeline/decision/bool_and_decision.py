from morning.logging import logger


class BoolAndDecision:
    def __init__(self, and_input_count, trade_count):
        self.and_input_count = and_input_count
        self.trade_count = trade_count
        self.decision = {}
        self.queue = None
        self.bought = False
        self.bidask_table = []

    def set_output(self, next_ele):
        pass

    def set_environ(self, target, queue):
        # self.target = target
        self.queue = queue

    def received(self, datas):
        if self.queue is None or len(datas) == 0:
            logger.warning(self.__class__.__name__, 'No queue error')
            return
        elif not self.bought and self.trade_count == 0:
            return # Already done today trade

        for d in datas:
            if d['name'] == 'DeliverBidAsk':
                self.bidask_table = d['value']
                return
            else:
                self.decision[d['name']] = d
        
        if len(self.decision) >= self.and_input_count:
            result = all([k['value'] for k in self.decision.values()])
            stream_name = datas[-1]['stream']
            value = 0
            if len(self.bidask_table) > 0 and stream_name == 'DatabaseTick':
                # Backtesting using tick
                value = self.bidask_table[2] if result else self.bidask_table[7]
            else:
                # Unknown purpose
                value = datas[-1]['value']
            
            target, date = datas[-1]['target'], datas[-1]['date']

            # currently not allow duplicated trade
            if not self.bought and result:
                self.queue_put_nowait({ 'target': target, 'date': date,
                                       'result': result, 'value': value})
                self.bought = True
            elif self.bought and not result:
                self.bought = False
                self.queue_put_nowait({ 'target': target, 'date': date,
                                    'result': result, 'value': value})
                self.trade_count -= 1
