from morning.logging import logger


class BoolAndDecision:
    def __init__(self, and_input_count, trade_count):
        self.and_input_count = and_input_count
        self.trade_count = trade_count
        self.next_elements = None
        self.decision = {}
        self.target = ''
        self.queue = None
        self.bought = False
        self.bidask_table = []
        self.time = 0

    def set_output(self, next_ele):
        pass

    def set_environ(self, target, queue):
        self.target = target
        self.queue = queue

    def received(self, datas):
        current_price = 0
        for d in datas:
            if d['type'] == 'BidAsk':
                self.bidask_table = d['value']
                self.time = d['time']
                return
            else:
                self.decision[d['name']] = d['value'] == 'True'
                current_price = d['price']
        
        if len(self.decision) >= self.and_input_count:
            result = all(self.decision.values())

            if self.queue and len(self.bidask_table) > 0:
                if self.bought and self.time > 150000:
                    self.queue.put_nowait(self.target + ':' + 'SELL:' + str(self.bidask_table[7]) + ':' + str(self.time))
                    self.bought = False
                elif result: # Use third ask bid price
                    if self.trade_count > 0:
                        self.queue.put_nowait(self.target + ':' + 'BUY:' + str(self.bidask_table[2]) + ':' + str(self.time))
                        self.trade_count -= 1
                        self.bought = True
                else:
                    if self.bought:
                        self.queue.put_nowait(self.target + ':' + 'SELL:' + str(self.bidask_table[7]) + ':' + str(self.time))
                        self.bought = False
            elif self.queue:
                if result:
                    if self.trade_count > 0:
                        self.queue.put_nowait(self.target + ':' + 'BUY:' + str(current_price) + ':0')
                        self.trade_count -= 1
                        self.bought = True
                else:
                    if self.bought:
                        self.queue.put_nowait(self.target + ':' + 'SELL:' + str(current_price) + ':0')
                        self.bought = False