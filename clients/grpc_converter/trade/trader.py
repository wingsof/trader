from gevent import monkey
monkey.patch_all()

import gevent
import grpc
import grpc.experimental.gevent as grpc_gevent
grpc_gevent.init_gevent()


import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 1))))

from gevent.queue import Queue
import stock_provider_pb2_grpc
import stock_provider_pb2 as stock_provider

from google.protobuf.empty_pb2 import Empty
import spread as sp
import account
import markettime
import simulstatus
import trademachine

from datetime import datetime


stub = None
spread_dict = dict()
order_queue = Queue()


# for simulation
def tick_subscriber():
    response = stub.ListenCybosTickData(Empty())
    for msg in response:
        if msg.code not in spread_dict:
            spread_dict[msg.code] = sp.Spread(msg.code, order_callback)

        spread_dict[msg.code].set_price_info(msg.buy_or_sell, msg.current_price, msg.bid_price, msg.ask_price, msg.market_type)
        trademachine.tick_arrived(msg.code, msg)


def bidask_subscriber():
    response = stub.ListenCybosBidAsk(Empty())
    for msg in response:
        if msg.code not in spread_dict:
            spread_dict[msg.code] = sp.Spread(msg.code, order_callback)

        spread_dict[msg.code].set_spread_info(msg.bid_prices, msg.ask_prices, msg.bid_remains, msg.ask_remains)
        trademachine.bidask_arrived(msg.code, msg)


def order_callback(result):
    stub.ReportOrderResult(stock_provider.OrderResult(report=result, current_balance=account.get_balance()))
    print('report order result')


def handle_order():
    while True:
        data = order_queue.get(True)

        if data.code not in spread_dict:
            if data.method == stock_provider.OrderMethod.TRADE_IMMEDIATELY:
                print(data.code, 'has no spread')
                continue

            spread_dict[data.code] = sp.Spread(data.code, order_callback)

        if not spread_dict[data.code].has_company_name():
            cname = stub.GetCompanyName(stock_provider.StockCodeQuery(code=data.code))
            spread_dict[data.code].set_company_name(cname.company_name)

        spread_dict[data.code].add_order(account.get_balance(), data)


def trade_subscriber():
    response = stub.ListenTraderMsg(Empty())
    for msg in response:
        print(msg.msg_type, msg.order_msg)
        if msg.msg_type == stock_provider.TradeMsgType.ORDER_MSG:
            order_queue.put_nowait(msg.order_msg)
        elif msg.msg_type == stock_provider.TradeMsgType.GET_BALANCE:
            stub.ReportOrderResult(stock_provider.OrderResult(current_balance=account.get_balance()))


def run():
    global stub
    with grpc.insecure_channel('localhost:50052') as channel:  
        subscribe_handlers = []
        stub = stock_provider_pb2_grpc.StockStub(channel)
        account._stub = stub
        subscribe_handlers.append(gevent.spawn(tick_subscriber))
        subscribe_handlers.append(gevent.spawn(bidask_subscriber))
        subscribe_handlers.append(gevent.spawn(trade_subscriber))
        subscribe_handlers.append(gevent.spawn(handle_order))
        subscribe_handlers.append(gevent.spawn(markettime.handle_time, stub))
        subscribe_handlers.append(gevent.spawn(simulstatus.simulation_subscriber, stub))
        subscribe_handlers.append(gevent.spawn(trademachine.run_trade, stub))
        subscribe_handlers.append(gevent.spawn(trademachine.handle_cybos_order, stub))
        subscribe_handlers.append(gevent.spawn(trademachine.handle_simulation_order))
        simulstatus.init_status(stub)

        gevent.joinall(subscribe_handlers)


if __name__ == '__main__':
    run()
