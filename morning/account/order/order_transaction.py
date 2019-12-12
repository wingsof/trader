from morning.cybos_api.trade_util import TradeUtil
from morning.cybos_api.order import Order
from morning.logging import logger

from PyQt5.QtCore import QTimer, QObject, pyqtSlot
from datetime import datetime, timedelta


class OrderTransaction(QObject):
    #@pyqtSlot()
    def __init__(self):
        super().__init__()

        trade_util = TradeUtil()
        self.account_num = trade_util.get_account_number()
        self.account_type = trade_util.get_account_type()

        self.order_wait_queue = dict()  # key: code, value: dict(date, is_buy, quantity, price)
        self.on_market_queue = dict() # key: code, value: [date, quantity, is_buy, price]
        self.long_list = dict() # key: code, value: quantity
        self.order = Order(self.account_num, self.account_type, self)

    def make_order(self, code, price, quantity, is_buy):
        if not is_buy:
            # get quantity from long_list
            pass

        status, msg = self.order.process(code, quantity, self.account_num, self.account_type,
                                        price, is_buy)

        if status != 0:
            logger.error(code, 'process error', msg)
        else:
            logger.print('ORDER process', code, msg)
            self.order_wait_queue[code] = {
                'date': datetime.now(), 'order_type': is_buy, 
                'quantity': quantity, 'price': price}
            QTimer.singleShot(3000, self._check_order_wait_queue)
            # should check time to prevent to throw new order away

    @pyqtSlot()
    def _check_order_wait_queue(self):
        remove_keys = []
        for k, v in self.order_wait_queue.items():
            if datetime.now() - v['date'] > timedelta(seconds=10):
                logger.error('Order queue not processed(will be removed)', k)
                remove_keys.append(k)

        for k in remove_keys:
            self.order_wait_queue.pop(k, None)

    @pyqtSlot()
    def _check_on_market_queue(self):
        # make a cancel order when exceed 10 second
        pass

    def handle_queued(self, code, is_buy, result):
        if code in self.order_wait_queue:
            order_wait_item = self.order_wait_queue[code]
            if result['quantity'] == order_wait_item['quantity'] and is_buy == order_wait_item['order_type']:
                self.on_market_queue['code'] = {
                'date': order_wait_item['date'], 'order_type': is_buy, 
                'quantity': result['quantity'], 'price': result['price']}
                self.order_wait_queue.pop(code, None)
                QTimer.singleShot(10000, self._check_on_market_queue)
            else:
                logger.error('wait queue and order event differ', 
                                result['quantity'], order_wait_item['quantity'],
                                is_buy, order_wait_item['order_type'])
        else:
            logger.error('code is not in order wait queue', code)

    def handle_traded(self, code, is_buy, result):
        if code in self.on_market_queue:
            on_market_item = self.on_market_queue[code]
            traded_quantity = result['quantity']
            if on_market_item['quantity'] == traded_quantity:
                # if buy then add it to long_list and remove it from on_market
                # else remove it from both long_list and on_market
                pass
            else:
                # if buy then add it to long_list and do not remove it from on_market
                # else remove part of it from long_list and on_market
                pass
        else:
            logger.error('code is not in on market queue', code)

    def order_event(self, result):
        # event from CpConclusion
        logger.print('ORDER EVENT', str(result))
        is_buy = result['order_type'] == '2'
        code = result['code']

        if result['flag'] == '4':   # Queued
            handle_queued(code, is_buy, result)
        elif result['flag'] == '1': # Traded
            handle_traded(code, is_buy, result)
        elif result['flag'] == '2': # Confirmed
            # when canceled or editied
            pass
        else:
            # Is there anything to recover state
            logger.print('ORDER EVENT ERROR', str(result))

        """
        result = {
            'flag': flag,  flag '1': done, '2': ok, '3': denied, '4':queued'
            'code': code,
            'order_num': order_num,
            'quantity': quantity,
            'price': price,
            'order_type': order_type,  buy/sell
            'total_quantity': total_quantity   count of stock left
        }
        """