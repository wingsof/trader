import gevent
from gevent.queue import Queue
from google.protobuf.empty_pb2 import Empty
import stock_provider_pb2 as stock_provider
import simulstatus
import markettime
import account
from datetime import timedelta


request_list = []
order_list = []
stock_long_dict = {}
trade_queue = Queue()
simulation_queue = Queue()
order_number = 111110



def get_order_number():
    global order_number
    order_number += 1
    return str(order_number) 


def move_to_order_list(cybos_order, msg):
    order_list.append(cybos_order)
    if cybos_order in request_list:
        request_list.remove(cybos_order)
    cybos_order.set_submitted(msg)


def cancel_order_list(cybos_order, msg):
    order_list.remove(cybos_order)
    cybos_order.set_submitted(msg)


def request_order(order_obj):
    # return value (result, msg)
    request_list.append(order_obj)
    if not simulstatus.is_simulation():
        pass # send cybos command return result, remove from request_list if get failed, 
    else:
        if order_obj.is_buy and (order_obj.price * order_obj.quantity > account.get_balance()):
            return -1, 'Not enough balance'
        else:
            account.pay_for_stock(order_obj.quantity * order_obj.price)
            trade_queue.put_nowait(order_obj)

    return 0, ''


def request_cancel(order_obj):
    found = False
    for order in order_list:
        if order == order_obj:
            found = True
            break
    
    if not found:
        return False

    order_list.remove(order_obj)
    if simulstatus.is_simulation(): 
        trade_queue.put_nowait(order_obj)
    else:
        pass # send cancel and remove it when get confirm

    return True


def request_modify(order_obj):
    pass


def run_trade(stub):
    while True:
        data = trade_queue.get(True)
        t = markettime.get_current_datetime()

        while markettime.get_current_datetime() - t < timedelta(seconds=3):
            gevent.sleep(0.1)

        order_obj = data.get_cybos_order_result()
        order_obj.order_number = str(get_order_number())
        order_obj.total_quantity = get_total_quantity(data.code)
        order_obj.flag = stock_provider.OrderStatusFlag.STATUS_SUBMITTED
        move_to_order_list(data, order_obj)
            

def tick_arrived(code, msg):
    if not simulstatus.is_simulation():
        return

    for order in order_list:
        if order.code == code:
            if order.order_type == stock_provider.OrderType.CANCEL:
                order_obj = order.get_cybos_order_result()
                add_total_quantity(order.code, -order.quantity)
                order_obj.total_quantity = get_total_quantity(order.code)
                order_obj.flag = stock_provider.OrderStatusFlag.STATUS_CONFIRM
                simulation_queue.put_nowait(order_obj)
            elif order.order_type == stock_provider.OrderType.MODIFY:
                pass
            else:
                if order.quantity == 0:
                    continue

                if order.is_buy:
                    if order.price >= msg.ask_price:
                        order_obj = order.get_cybos_order_result()
                        add_total_quantity(order.code, order.quantity)
                        order_obj.total_quantity = get_total_quantity(order.code)
                        order_obj.price = msg.ask_price
                        order_obj.flag = stock_provider.OrderStatusFlag.STATUS_TRADED
                        simulation_queue.put_nowait(order_obj)
                else:
                    if order.price <= msg.bid_price:
                        order_obj = order.get_cybos_order_result()
                        add_total_quantity(order.code, -(order.quantity))
                        order_obj.total_quantity = get_total_quantity(order.code)
                        order_obj.price = msg.bid_price
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
            if (cybos_order.code == msg.code and
                                cybos_order.price == msg.price and
                                cybos_order.quantity == msg.quantity and
                                cybos_order.is_buy == msg.is_buy):
                move_to_order_list(r)
                break
    elif msg.flag == stock_provider.OrderStatusFlag.STATUS_TRADED:
        for cybos_order in order_list:
            if cybos_order.order_num == msg.order_number and cybos_order.quantity > 0:
                if not cybos_order.is_buy:
                    account.pay_for_stock(-(msg.quantity * msg.price))    

                cybos_order.set_traded(msg)
                break
    elif msg.flag == stock_provider.OrderStatusFlag.STATUS_CONFIRM:
        for cybos_order in order_list:
            if cybos_order.order_num == msg.order_number:
                if cybos_order.method == stock_provider.OrderMethod.TRADE_CANCEL:
                    order_list.remove(cybos_order)
                    cybos_order.set_confirmed(msg)
                    # TODO: buy and cancel then set account
                    break
                elif cybos_order.method == stock_provider.OrderMethod.TRADE_MODIFY:
                    # TODO: buy and modify then set account
                    pass
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

