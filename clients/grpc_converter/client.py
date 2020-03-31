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
from google.protobuf.empty_pb2 import Empty

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


def get_minute_data(stub):
    from_datetime = Timestamp()
    from_datetime.FromSeconds(int(datetime.timestamp(datetime(2020, 3, 18))))
    until_datetime = Timestamp()
    until_datetime.FromSeconds(int(datetime.timestamp(datetime(2020, 3, 20))))
    query = stock_provider_pb2.StockQuery(code='A005930',
        from_datetime = from_datetime,
        until_datetime = until_datetime)
    response = stub.GetMinuteData(query)
    print('len', len(response.day_data))
    for data in response.day_data:
        pass#print(data)


def tick_subscriber(stub):
    query = Empty()
    i = 0
    response = stub.ListenCybosTickData(query)
    for msg in response:
        i += 1
        print('tick', i)


def subscribe_stock(code, stub):
    query = stock_provider_pb2.StockCodeQuery(code=code)
    response = stub.RequestCybosTickData(query)


def subscribe_bidask(code, stub):
    query = stock_provider_pb2.StockCodeQuery(code=code)
    response = stub.RequestCybosBidAsk(query)


def run():
    global _STUB
    with grpc.insecure_channel('localhost:50052') as channel:
        _STUB = stock_provider_pb2_grpc.StockStub(channel)
        get_day_data(_STUB)
        get_minute_data(_STUB)
        gevent.sleep(10)
        subscribe_stock('A005930', _STUB)
        subscribe_stock('A000660', _STUB)
        
        gevent.joinall([gevent.spawn(tick_subscriber, _STUB)])
    print('exit')

if __name__ == '__main__':
    run()
