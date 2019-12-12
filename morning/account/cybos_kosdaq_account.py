from morning.cybos_api.trade_util import TradeUtil
from morning.cybos_api.balance import get_balance
from morning.pipeline.stream.cybos.stock.bidask_tick import CybosBidAskTick
from morning.account.order.order_transaction import OrderTransaction
from morning.logging import logger

from datetime import datetime


ask_keys = ['first_ask_price', 'second_ask_price', 'third_ask_price', 
                    'fourth_ask_price', 'fifth_ask_price']
bid_keys = ['first_bid_price', 'second_bid_price', 'third_bid_price', 
                    'fourth_bid_price', 'fifth_bid_price']


class CybosKosdaqAccount:
    EXPECTED_DAY_MAX_COUNT = 16

    def __init__(self, save_to_file = ''):
        trade_util = TradeUtil()
        self.montoring_bidask = []
        self.account_balance = get_balance(self.account_num, self.account_type)
        self.one_shot_amount = int(self.account_balance / CybosKosdaqAccount.EXPECTED_DAY_MAX_COUNT)
        self.bidask_table = dict()
        self.order_transaction = OrderTransaction()

    def set_bidask_monitoring(self, code):
        bidask = CybosBidAskTick()
        bidask.set_output(self)
        bidask.set_target(code)
        
        self.montoring_bidask.append(bidask)

    def received(self, bidask_datas):
        for d in bidask_datas:
            self.bidask_table[d['target']] = {
                'ask': [d[k] for k in ask_keys],
                'bid': [d[k] for k in bid_keys]}        

    def transaction(self, msg):
        buy, code, price = msg['result'], msg['target'], msg['value']
        price = int(price)
        if code not in self.bidask_table:
            logger.error(code, 'is not in BIDASK Table')
            return

        bidask_str = 'ask' if buy else 'bid'
        process_price = self.bidask_table[code][bidask_str][4]
        # does not support split selling
        quantity= int(self.one_shot_amount / process_price) if buy else 0
        self.order_transaction.make_order(code, process_price, quantity, buy)

        
        