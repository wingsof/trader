import gevent
from utils import trade_logger as logger
from clients.scalping_by_amount import price_info
from utils import trade_logger as logger


MAX_SLOT = 3


class SellMethod:
    def __init__(self, reader, code_info, market_status, average_price, qty, handler):
        self.reader = reader
        self.code_info = code_info
        self.market_status = market_status
        self.average_price = average_price
        self.minimum_profit_price = self.average_price * 1.0025
        self.cut_price = self.average_price * 0.99
        self.qty = qty
        self.current_bid = -1
        self.slots = None
        self.bidask_price_unit = -1
        self.previous_current_bid = -1
        self.immediate_sell_price = -1
        self.bidask_handler = handler

    def get_code(self):
        return self.code_info['code']

    def get_cut_price(self):
        return self.cut_price

    def sell_immediately(self):
        pass

    def get_current_bidask_unit(self):
        return self.bidask_price_unit

    def get_top_bid(self):
        return self.current_bid

    def decrement_quantity(self, qty):
        self.qty -= qty

    def get_slots(self):
        return self.slots

    def is_finished(self):
        return self.qty == 0

    def set_quantity(self, qty):
        self.qty = qty

    def get_current_quantity(self):
        return self.qty

    def get_immediate_sell_price(self):
        return self.immediate_sell_price

    def get_minimum_profit_price(self):
        return self.minimum_profit_price

    def ba_data_handler(self, code, tick_data):
        self.current_bid = tick_data['first_bid_price']

        if self.previous_current_bid != self.current_bid:
            logger.info('%s FIRST BID CHANGED TO %d', code, self.current_bid)
        self.bidask_price_unit = price_info.get_ask_bid_price_unit(self.current_bid, self.code_info['is_kospi'])
        self.immediate_sell_price = price_info.get_immediate_sell_price(tick_data, self.qty, self.bidask_price_unit)
        self.slots = price_info.create_slots(
                    self.code_info['yesterday_close'],
                    self.current_bid,
                    self.code_info['today_open'],
                    self.code_info['is_kospi'])
        self.bidask_handler(code, tick_data)
        self.previous_current_bid = self.current_bid

    def get_current_available_price_slots(self):
        price_slot = price_info.upper_available_empty_slots(self.slots)
        return list(filter(lambda x: x > self.minimum_profit_price, price_slot))


    def get_price_slots(self, slots, mprice, qty):
        price_slot = price_info.upper_available_empty_slots(slots)
        profit_slot = list(filter(lambda x: x > mprice, price_slot))
        if len(price_slot) == 0:
            logger.error('NO PROFIT SLOT')
            return []

        logger.info('AVAILABLE PROFIT SLOT len(%d), START FROM %d',
                    len(profit_slot), profit_slot[0])
        if len(profit_slot) > MAX_SLOT:
            profit_slot = profit_slot[:MAX_SLOT]
        
        while qty / len(profit_slot) < 0:
            profit_slot = profit_slot[:-1]

        return profit_slot
