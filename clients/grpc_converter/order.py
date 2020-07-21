import gevent
import math
import simulstatus
import markettime
import trademachine
import account
from datetime import timedelta

import stock_provider_pb2 as sprovider


class Order:
    INTERNAL_ID_PREFIX='I'
    ID_NUM=0

    def get_id_number():
        Order.ID_NUM += 1
        return str(Order.ID_NUM)

    def __init__(self, code, order, callback):
        self.code = code
        self.status = sprovider.OrderStatusFlag.STATUS_REGISTERED
        self.is_buy = order.is_buy
        self.last_update_time = markettime.get_current_datetime()
        self.callback = callback
        self.qty = order.quantity
        self.method = order.method
        self.price = order.price
        self.hold_price = 0
        self.hold_qty = 0
        self.id = Order.INTERNAL_ID_PREFIX + code + Order.get_id_number()
        trademachine.request_order(self.code, self.price, self.qty, self.is_buy)


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

