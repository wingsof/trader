from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSlot

from morning.cybos_api.trade_util import TradeUtil
from morning.cybos_api.balance import get_balance
from morning.pipeline.stream.cybos.stock.bidask_tick import CybosBidAskTick
from morning.account.order.order_transaction import OrderTransaction
from morning.logging import logger




ask_keys = ['first_ask_price', 'second_ask_price', 'third_ask_price', 
                    'fourth_ask_price', 'fifth_ask_price']
bid_keys = ['first_bid_price', 'second_bid_price', 'third_bid_price', 
                    'fourth_bid_price', 'fifth_bid_price']


class CybosKosdaqAccount(QObject):
    EXPECTED_DAY_MAX_COUNT = 16

    def __init__(self, save_to_file = ''):
        super().__init__()
        trade_util = TradeUtil()
        self.montoring_bidask = []
        self.account_balance = get_balance(trade_util.get_account_number(), trade_util.get_account_type())
        self.one_shot_amount = int(self.account_balance / CybosKosdaqAccount.EXPECTED_DAY_MAX_COUNT)
        self.bidask_table = dict()
        self.order_transaction = OrderTransaction(self)

    def get_ask_price(self, code, n_th):
        if code not in self.bidask_table or n_th > 4:
            logger.error(code, n_th, ' get_ask_price error')
            return 0
        
        return self.bidask_table[code]['ask'][n_th]

    def set_bidask_monitoring(self, code):
        bidask = CybosBidAskTick()
        bidask.set_output(self)
        bidask.set_target(code)
        
        self.montoring_bidask.append(bidask)
        logger.print('START Monitoring BA', code)

    def received(self, bidask_datas):
        #logger.print('received', bidask_datas)
        for d in bidask_datas:
            self.bidask_table[d['target']] = {
                'ask': [d[k] for k in ask_keys],
                'bid': [d[k] for k in bid_keys]}        

    @pyqtSlot(object)
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

        if buy and quantity == 0:
            logger.error('not enough to buy shares', self.one_shot_amount, process_price)
        else:
            self.order_transaction.make_order(code, process_price, quantity, buy)
            return process_price, quantity

        return 0, 0

        
        