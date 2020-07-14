from gevent import monkey
monkey.patch_all()

import gevent
import grpc
import grpc.experimental.gevent as grpc_gevent
grpc_gevent.init_gevent()

import stock_provider_pb2_grpc
import stock_provider_pb2

from google.protobuf.empty_pb2 import Empty


def tick_subscriber(stub):
    query = Empty()
    response = stub.ListenCybosTickData(query)
    for msg in response:
        pass

def trade_subscriber(stub):
    query = Empty()
    response = stub.ListenTraderMsg(query)
    for msg in response:
        print(msg.price)


def run():
    with grpc.insecure_channel('localhost:50052') as channel:  
        subscribe_handlers = []
        _stub = stock_provider_pb2_grpc.StockStub(channel)
        subscribe_handlers.append(gevent.spawn(tick_subscriber, _stub))
        subscribe_handlers.append(gevent.spawn(trade_subscriber, _stub))
        gevent.joinall(subscribe_handlers)


if __name__ == '__main__':
    run()
