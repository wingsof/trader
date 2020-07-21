import gevent
from gevent.queue import Queue
from google.protobuf.empty_pb2 import Empty
import stock_provider_pb2 as stock_provider
import simulstatus
import markettime
from datetime import timedelta


request_list = []
order_list = []
stock_long_dict = {}
trade_queue = Queue()
simulation_queue = Queue()
order_number = 111110


class CybosOrder:
    ORDER=1
    MODIFY=2
    CANCEL=3

    def __init__(self, request_type, code, price, quantity, is_buy, callback, order_num = ''):
        self.request_type = request_type
        self.status = stock_provider.OrderStatusFlag.STATUS_REGISTERED
        self.code = code
        self.price = price
        self.quantity = quantity
        self.left_count = quantity
        self.is_buy = is_buy
        self.callback = callback
        self.order_num = order_num

    def set_traded(self, order_msg):
        print('Traded', order_msg)
        self.left_count -= order_msg.quantity
        if self.left_count == 0:
            order_list.remove(self)
        self.status = order_msg.flag


    def set_submitted(self, order_msg):
        print('Get Submit', order_msg)
        if self.request_type == CybosOrder.ORDER:
            self.order_num = order_msg.order_number
            self.status = order_msg.flag

    def set_confirmed(self, order_msg):
        pass

    def set_denied(self, order_msg):
        pass
    
    def get_order_object(self):
        return stock_provider.CybosOrderResult(flag=self.status,
                                               code=self.code,
                                               order_number=self.order_num,
                                               quantity=self.quantity,
                                               price=self.price,
                                               is_buy=self.is_buy,
                                               total_quantity=0)


def get_order_number():
    global order_number
    order_number += 1
    return str(order_number) 


def move_to_order_list(cybos_order, msg):
    order_list.append(cybos_order)
    request_list.remove(cybos_order)
    cybos_order.set_submitted(msg)


def cancel_order_list(cybos_order, msg):
    order_list.remove(cybos_order)
    cybos_order.set_submitted(msg)


def request_order(order_obj):
    # return value (result, msg)
    cybos_order = CybosOrder(CybosOrder.ORDER, code, price, quantity, is_buy, callback)

    request_list.append(cybos_order)
    if not simulstatus.is_simulation():
        pass # send cybos command return result, remove from request_list if get failed, 
    else:
        trade_queue.put_nowait(cybos_order)

    return 0, ''


def request_cancel(code, order_num, quantity, is_buy, callback):
    original_order = None
    for order in order_list:
        if order.num == order_num:
            original_order = order
            break

    if original_order is not None:
        original_order.request_type = CybosOrder.CANCEL
        original_order.status = stock_provider.OrderStatusFlag.STATUS_REGISTERED
        if simulstatus.is_simulation(): 
            trade_queue.put_nowait(original_order)
        else:
            pass # send cancel and remove it when get confirm
    else:
        return False

    return True


def request_modify(code, order_num, price, is_buy, callback):
    pass


def run_trade(stub):
    while True:
        data = trade_queue.get(True)
        t = markettime.get_current_datetime()

        while markettime.get_current_datetime() - t < timedelta(seconds=3):
            gevent.sleep(0.1)

        if data.request_type == CybosOrder.ORDER:
            order_obj = data.get_order_object()
            order_obj.order_number = str(get_order_number())
            order_obj.total_quantity = get_total_quantity(data.code)
            order_obj.flag = stock_provider.OrderStatusFlag.STATUS_SUBMITTED
            move_to_order_list(data, order_obj)
        elif data.request_type == CybosOrder.CANCEL:
            order_obj = data.get_order_object()
            order_obj.total_quantity = 0
            order_obj.flag = stock_provider.OrderStatusFlag.STATUS_SUBMITTED
            cancel_order_list(data, order_obj)
            

def tick_arrived(code, msg):
    if not simulstatus.is_simulation():
        return

    for order in order_list:
        if order.code == code:
            if order.is_buy:
                if order.price >= msg.bid_price:
                    order_obj = order.get_order_object()
                    add_total_quantity(order.code, order.quantity)
                    order_obj.total_quantity = get_total_quantity(order.code)
                    order_obj.flag = stock_provider.OrderStatusFlag.STATUS_TRADED
                    simulation_queue.put_nowait(order_obj)
            else:
                if order.price <= msg.ask_price:
                    order_obj = order.get_order_object()
                    add_total_quantity(order.code, -(order.quantity))
                    order_obj.total_quantity = get_total_quantity(order.code)
                    order_obj.flag = stock_provider.OrderStatusFlag.STATUS_TRADED
                    simulation_queue.put_nowait(order_obj)


def get_total_quantity(code):
    if code not in stock_long_dict:
        stock_long_dict[code] = 0

    return stock_long_dict[code]


def add_total_quantity(code, quantity):
    if code not in stock_long_dict:
        stock_long_dict[code] = 0
    stock_long_dict[code] += quantity


def bidask_arrived(code, msg):
    pass


def handle_server_order(msg):
    if msg.flag == stock_provider.OrderStatusFlag.STATUS_SUBMITTED:
        for cybos_order in request_list:
            if len(cybos_order.order_num) > 0:
                if cybos_order.order_num == msg.order_number:
                    break
            else:
                if (cybos_order.code == msg.code and
                        cybos_order.price == msg.price and
                        cybos_order.quantity == msg.quantity and
                        cybos_order.is_buy == msg.is_buy):
                    move_to_order_list(r)
                    break
    elif msg.flag == stock_provider.OrderStatusFlag.STATUS_TRADED:
        for cybos_order in order_list:
            if cybos_order.order_num == msg.order_number:
                cybos_order.set_traded(msg)
                break
    elif msg.flag == stock_provider.OrderStatusFlag.STATUS_CONFIRMED:
        for cybos_order in order_list:
            if cybos_order.order_num == msg.order_number:
                cybos_order.set_confirmed(msg)
                break
    elif msg.flag == stock_provider.OrderStatusFlag.STATUS_DENIED:
        for cybos_order in order_list:
            if cybos_order.order_num == msg.order_number:
                cybos_order.set_denied(msg)
                break


def handle_simulation_order():
    while True:
        data = simulation_queue.get(True)
        handle_server_order(data)


def handle_cybos_order(stub):
    response = stub.ListenCybosOrderResult(Empty())
    for msg in response:
        handle_server_order(msg)

