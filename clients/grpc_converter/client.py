from gevent import monkey
monkey.patch_all()

import grpc
import grpc.experimental.gevent as grpc_gevent
grpc_gevent.init_gevent()


import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))

import gevent
from concurrent import futures
import stock_provider_pb2_grpc
import stock_provider_pb2
from datetime import datetime

from google.protobuf.timestamp_pb2 import Timestamp

_STUB = None

def get_day_data(stub):
    from_datetime = Timestamp()
    from_datetime.FromSeconds(int(datetime.timestamp(datetime(2020, 3, 18))))
    until_datetime = Timestamp()
    until_datetime.FromSeconds(int(datetime.timestamp(datetime(2020, 3, 20))))
    query = stock_provider_pb2.StockQuery(code='A005930',
        from_datetime = from_datetime,
        until_datetime = until_datetime)
    response = stub.GetDayData(query)
    print('len', len(response.day_data))
    for data in response.day_data:
        print(data)


def subscribe_stock(code, stub):
    query = stock_provider_pb2.StockCodeQuery(code=code)
    response = stub.SubscribeStock(query)
    for msg in response:
        pass
        #print('subscribe', msg)


def subscribe_bidask(code, stub):
    query = stock_provider_pb2.StockCodeQuery(code=code)
    response = stub.SubscribeBidAsk(query)
    for msg in response:
        print('biask', msg)


def run():
    global _STUB
    with grpc.insecure_channel('localhost:50052') as channel:
        _STUB = stock_provider_pb2_grpc.StockStub(channel)
        get_day_data(_STUB)
        subscriber1 = gevent.spawn(subscribe_stock, 'A005930', _STUB)
        subscriber2 = gevent.spawn(subscribe_stock, 'A000660', _STUB)
        subscriber3 = gevent.spawn(subscribe_bidask, 'A005930', _STUB)
        
        gevent.joinall([subscriber1, subscriber2, subscriber3])
    print('exit')

if __name__ == '__main__':
    run()
