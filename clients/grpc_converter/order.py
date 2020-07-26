import gevent
import math
import simulstatus
import markettime
import trademachine
import account
from datetime import timedelta
from google.protobuf.timestamp_pb2 import Timestamp

import stock_provider_pb2 as sp


class Order:
    INTERNAL_ID_PREFIX = 'I'
    ID_NUM = 0

    def get_id_number():
        Order.ID_NUM += 1
        return str(Order.ID_NUM)

    def __init__(self, code, cname, order_request, hold_price, callback):
        self.code = code
        self.company_name = cname
        self.status = sp.OrderStatusFlag.STATUS_REGISTERED
        self.is_buy = order_request.is_buy
        self.last_update_time = markettime.get_current_datetime()
        self.callback = callback
        self.quantity = order_request.quantity
        self.method = order_request.method
        self.price = order_request.price
        self.order_type = order_request.order_type
        self.internal_order_num = Order.INTERNAL_ID_PREFIX + code + Order.get_id_number()
        self.order_num = self.internal_order_num
        self.hold_price = hold_price
        
    def request(self):
        return trademachine.request_order(self)

    def change_order(self, order_msg):
        if order_msg.method != sp.OrderMethod.TRADE_UNKNOWN and order_msg.method != self.method:
            self.method = order_msg.method

        if order_msg.price != 0 and order_msg.price != self.price:
            self.price = order_msg.price

        if order_msg.quantity != 0 and order_msg.quantity != self.quantity:
            self.quantity = order_msg.quantity

        if self.status == sp.OrderStatusFlag.STATUS_REGISTERED:
            self.request()

        """
        if order_msg.method == sp.OrderMethod.TRADE_CANCEL:
            self.method = order_msg.method
            print('send request cancel')
            return trademachine.request_cancel(self)
        elif order_msg.method == sp.OrderMethod.TRADE_MODIFY:
            return trademachine.reqeust_modify(self) 
        """
        return True

    def set_submitted(self, msg):
        self.order_num = msg.order_number
        self.status = sp.OrderStatusFlag.STATUS_SUBMITTED
        self.callback(self.status, msg.is_buy, msg.price, msg.quantity, 0)

    def set_traded(self, msg):
        self.quantity -= msg.quantity
        self.price = msg.price
        self.status = sp.OrderStatusFlag.STATUS_TRADED
        self.callback(self.status, msg.is_buy, msg.price, msg.quantity, msg.total_quantity)

    def set_confirmed(self, msg):
        print('set confirm', msg.order_number)

    def get_cybos_order_result(self):
        return sp.CybosOrderResult(flag=self.status,
                                               code=self.code,
                                               order_number=self.order_num,
                                               quantity=self.quantity,
                                               price=self.price,
                                               is_buy=self.is_buy,
                                               total_quantity=0)

    def convert_to_report(self):
        lud = Timestamp()
        lud.FromDatetime(self.last_update_time)

        return sp.Report(code=self.code,
                         company_name=self.company_name,
                         is_buy=self.is_buy,
                         last_update_datetime=lud,
                         flag=self.status,
                         method=self.method,
                         price=self.price,
                         quantity=self.quantity,
                         hold_price=int(self.hold_price),
                         internal_order_num=self.internal_order_num,
                         order_num=self.order_num)

    def status_to_str(self):
        if self.status == 1:
            return 'Registerd'
        elif self.status == ord('1'):
            return 'Traded'
        elif self.status == ord('2'):
            return 'Confirm(CANCEL,MODIFY)'
        elif self.status == ord('3'):
            return 'Denied'
        elif self.status == ord('4'):
            return 'Submitted'
        return 'Unknown'

    def __str__(self):
        debug_str = '*' * 30 + '\n'
        debug_str += 'STATUS:' + self.status_to_str() + '\n'
        debug_str += 'IS_BUY: ' + str(self.is_buy) + '\n'
        debug_str += 'ORDER NUM: ' + str(self.order_num) + '\n'
        debug_str += 'ORDER TYPE: ' + str(self.order_type) + '\n'
        debug_str += 'PRICE: ' + str(self.price) + '\n'
        debug_str += 'QTY: ' + str(self.quantity) + '\n'
        debug_str += 'METHOD: ' + str(self.method) + '\n'
        debug_str += '*' * 30
        return debug_str
