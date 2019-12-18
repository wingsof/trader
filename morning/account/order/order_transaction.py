from PyQt5.QtCore import QTimer, QObject, pyqtSlot
from datetime import datetime, timedelta

from morning.cybos_api.trade_util import TradeUtil
from morning.cybos_api.order import Order
from morning.logging import logger
from morning.cybos_api.order_in_queue import OrderInQueue
from morning.cybos_api.cancel_order import CancelOrder
from morning.cybos_api.modify_order import ModifyOrder
from morning.trade_record import *

class OrderTransaction(QObject):
    NORMAL = 0
    CANCEL = 1
    MODIFY = 2

    def __init__(self, account_obj):
        super().__init__()

        self.account_obj = account_obj
        trade_util = TradeUtil()
        self.account_num = trade_util.get_account_number()
        self.account_type = trade_util.get_account_type()
        self.order_in_queue = OrderInQueue(self.account_num, self.account_type)

        self.order_wait_queue = dict()  # key: code, value: dict(date, is_buy, quantity, price)
        self.on_market_queue = dict() # key: code, value: [date, quantity, is_buy, price, order_number]
        self.long_list = dict() # key: code, value: quantity
        self.order = Order(self.account_num, self.account_type, self)

    def make_order(self, code, price, quantity, is_buy):
        if not is_buy:
            if code in self.long_list:
                quantity = self.long_list[code]
            else:
                logger.error(code, 'is not int long_list')
                return

        record_make_order(code, price, quantity, is_buy)
        status, msg = self.order.process(code, quantity, self.account_num, 
                                        self.account_type, price, is_buy)

        if status != 0:
            logger.error(code, 'process error', msg)
        else:
            logger.print('ORDER process', code, msg)
            self.order_wait_queue[code] = {
                'date': datetime.now(), 'order_type': is_buy, 
                'quantity': quantity, 'price': price}
            QTimer.singleShot(10000, self._check_order_wait_queue)
            # should check time to prevent to throw new order away

    @pyqtSlot()
    def _check_order_wait_queue(self):
        logger.print('check order wait timeout')
        remove_keys = []
        for k, v in self.order_wait_queue.items():
            if datetime.now() - v['date'] > timedelta(seconds=8):
                logger.error('Order queue not processed(will be removed)', k)
                remove_keys.append(k)

        for k in remove_keys:
            logger.print('remove key', k)
            self.order_wait_queue.pop(k, None)

    @pyqtSlot()
    def _check_on_market_queue(self):
        logger.print('check on market queue')
        orders = self.order_in_queue.request()
        # Use Cp5339 and verify not traded items
        for k, v in self.on_market_queue.items():
            if v['order_modify_type'] == OrderTransaction.NORMAL and datetime.now() - v['date'] > timedelta(seconds=8):
                in_bills = None
                for order in orders:
                    if order['number'] == v['order_number']:
                        in_bills = order
                        break
                if in_bills is None:
                    logger.error('Cannot find matched item in bills')
                    continue

                if v['order_type']: # BUY
                    cancel_order = CancelOrder(self.account_num, self.account_type)
                    record_cancel_order(k, v.copy())
                    cancel_order.cancel_order(v['order_number'], k, 0)
                    v['order_modify_type'] = OrderTransaction.CANCEL
                else:
                    # modify order to sell immediately
                    modify_order = ModifyOrder(self.account_num, self.account_type)
                    record_modify_order(k, v.copy())
                    order_new_num = modify_order.modify_order(v['order_number'], k, 0, self.account_obj.get_ask_price(k, 4))
                    order['number'] = order_new_num
                    v['order_modify_type'] = OrderTransaction.MODIFY
        
    def handle_queued(self, code, is_buy, result):
        if code in self.order_wait_queue:
            order_wait_item = self.order_wait_queue[code]
            if result['quantity'] == order_wait_item['quantity'] and is_buy == order_wait_item['order_type']:
                self.on_market_queue[code] = {'date': order_wait_item['date'], 
                                                'order_type': is_buy, 
                                                'order_number': result['order_number'],
                                                'quantity': result['quantity'], 
                                                'price': result['price'], 
                                                'order_modify_type': OrderTransaction.NORMAL}
                self.order_wait_queue.pop(code, None)
                QTimer.singleShot(10000, self._check_on_market_queue)
            else:
                logger.error('wait queue and order event differ', 
                                result['quantity'], order_wait_item['quantity'],
                                is_buy, order_wait_item['order_type'])
        else:
            logger.error('code is not in order wait queue', code)

    def handle_traded(self, code, is_buy, result):
        logger.print('handle_traded', code, is_buy)
        if code in self.on_market_queue:
            on_market_item = self.on_market_queue[code]
            traded_quantity = result['quantity']
            if on_market_item['quantity'] == traded_quantity:
                if is_buy:
                    self.long_list[code] = traded_quantity
                    self.on_market_queue.pop(code, None)
                else:
                    self.long_list.pop(code, None)
                    self.on_market_queue.pop(code, None)
            else:
                if code not in self.long_list:
                    self.long_list[code] = 0

                if is_buy:
                    self.long_list[code] += traded_quantity
                else:
                    self.long_list[code] -= traded_quantity
                on_market_item['quantity'] -= traded_quantity
            QTimer.singleShot(10000, self._check_on_market_queue)
        else:
            logger.error('code is not in on market queue', code)

    def handle_edited(self, code, is_buy, result):
        logger.print('handle_edited', code, is_buy)
        if code in self.on_market_queue:
            on_market_item = self.on_market_queue[code]
            if on_market_item['order_modify_type'] == OrderTransaction.CANCEL:
                if on_market_item['order_number'] != result['order_num']:
                    logger.error('TODO order number is not matched')
                self.on_market_queue.pop(code, None)
            elif on_market_item['order_modify_type'] == OrderTransaction.MODIFY:
                logger.print('ORDER MODIFY SUCCESS', str(result))
        else:
            logger.error('code is not in on market queue(editied)', code)

    def order_event(self, result):
        # event from CpConclusion
        logger.print('ORDER EVENT', str(result))
        is_buy = result['order_type'] == '2'
        code = result['code']

        if result['flag'] == '4':   # Queued
            self.handle_queued(code, is_buy, result)
        elif result['flag'] == '1': # Traded
            self.handle_traded(code, is_buy, result)
        elif result['flag'] == '2': # Confirmed
            self.handle_edited(code, is_buy, result)
        else:
            # Is there anything to recover state
            logger.print('ORDER EVENT ERROR', str(result))

        """
        result = {
            'flag': flag,  flag '1': done, '2': ok, '3': denied, '4':queued'
            'code': code,
            'order_number': order_num,
            'quantity': quantity,
            'price': price,
            'order_type': order_type,  buy/sell
            'total_quantity': total_quantity   count of stock left
        }
        """
