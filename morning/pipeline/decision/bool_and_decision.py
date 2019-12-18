from morning.logging import logger


class BoolAndDecision:
    def __init__(self, and_input_count, trade_count):
        self.and_input_count = and_input_count
        self.trade_count = trade_count
        self.decision = {}
        self.runner_callback = None
        self.bought = False
        self.bidask_table = []

    def finalize(self):
        pass

    def set_output(self, next_ele):
        pass

    def set_environ(self, runner_callback):
        self.runner = runner_callback

    def received(self, datas):
        if self.runner is None or len(datas) == 0:
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
        
        # TODO: Refactoring required
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

                if 'price' in datas[-1]:
                    value = datas[-1]['price']
                elif 'profit' in datas[-1]:
                    value = datas[-1]['profit']
            
            target, date = datas[-1]['target'], datas[-1]['date']
            strategy = datas[-1]['name']

            if not self.bought and result:
                msg = { 'target': target, 'date': date, 'stream': stream_name,
                        'strategy': strategy, 'result': result, 'value': value}
                self.runner(msg)
                self.bought = True
            elif self.bought and not result:
                msg = { 'target': target, 'date': date, 'stream': stream_name,
                        'strategy': strategy, 'result': result, 'value': value}
                if 'highest' in datas[0]:
                    msg['highest'] = datas[0]['highest']
                self.bought = False
                self.trade_count -= 1
                self.runner(msg)
