from gevent import monkey
monkey.patch_all()

import grpc
import grpc.experimental.gevent as grpc_gevent
grpc_gevent.init_gevent()

import time

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))

import gevent
from concurrent import futures
import stock_provider_pb2_grpc
import stock_provider_pb2
from datetime import datetime

from google.protobuf import timestamp_pb2
from google.protobuf.empty_pb2 import Empty

_STUB = None

def get_day_data(stub):
    from_datetime = timestamp_pb2.Timestamp()
    from_datetime.FromSeconds(int(datetime.timestamp(datetime(2020, 3, 18))))
    until_datetime = timestamp_pb2.Timestamp()
    until_datetime.FromSeconds(int(datetime.timestamp(datetime(2020, 3, 20))))
    query = stock_provider_pb2.StockQuery(code='A005930',
        from_datetime = from_datetime,
        until_datetime = until_datetime)
    response = stub.GetDayData(query)
    print('len', len(response.day_data))
    for data in response.day_data:
        print(data)


def send_stock_selection(stub, code):
    until_datetime = timestamp_pb2.Timestamp()
    until_datetime.FromDatetime(datetime(2020, 6, 11))
    query = stock_provider_pb2.StockSelection(code=code, count_of_days=200, until_datetime=until_datetime)
    stub.SetCurrentStock(query)

def get_minute_data(stub):
    from_datetime = timestamp_pb2.Timestamp()
    from_datetime.FromSeconds(int(datetime.timestamp(datetime(2020, 3, 18))))
    until_datetime = timestamp_pb2.Timestamp()
    until_datetime.FromSeconds(int(datetime.timestamp(datetime(2020, 3, 20))))
    query = stock_provider_pb2.StockQuery(code='A005930',
        from_datetime = from_datetime,
        until_datetime = until_datetime)
    response = stub.GetMinuteData(query)
    print('len', len(response.day_data))
    for data in response.day_data:
        pass#print(data)


def start_simulation(stub):
    from_datetime = timestamp_pb2.Timestamp()
    #from_datetime.FromDatetime(datetime(2020, 6, 12, 9, 3, 12))
    from_datetime.FromDatetime(datetime(2020, 6, 12, 10, 1, 0))
    #from_datetime.FromDatetime(datetime(2020, 6, 12, 8, 59))
    simulation_argument = stock_provider_pb2.SimulationArgument(from_datetime=from_datetime)
    response = stub.StartSimulation(simulation_argument) 
    for msg in response:
        i += 1


def tick_subscriber(stub):
    query = Empty()
    i = 0
    response = stub.ListenCybosTickData(query)
    for msg in response:
        i += 1
        print('tick', i, msg.tick_date.ToDatetime())


def bidask_subscriber(stub):
    query = Empty()
    i = 0
    response = stub.ListenCybosBidAsk(query)
    for msg in response:
        i += 1
        print('bidask', i, msg.tick_date.ToDatetime())


def subject_subscriber(stub):
    query = Empty()
    i = 0
    response = stub.ListenCybosSubject(query)
    for msg in response:
        i += 1
        print('subject', i, msg.tick_date.ToDatetime())


def subscribe_stock(code, stub):
    query = stock_provider_pb2.StockCodeQuery(code=code)
    response = stub.RequestCybosTickData(query)


def subscribe_bidask(code, stub):
    query = stock_provider_pb2.StockCodeQuery(code=code)
    response = stub.RequestCybosBidAsk(query)


def time_listener(stub):
    query = Empty()
    i = 0
    print('ListenCurrentTime')
    response = stub.ListenCurrentTime(query)
    for msg in response:
        pass #print(msg.ToDatetime())


def run():
    global _STUB
    with grpc.insecure_channel('localhost:50052') as channel:
        _STUB = stock_provider_pb2_grpc.StockStub(channel)
        #result = _STUB.GetYesterdayTopAmountCodes(Empty())
        #print('codes', result.codelist)
        #get_day_data(_STUB)
        #get_minute_data(_STUB)
        gevent.joinall([gevent.spawn(start_simulation, _STUB)])
        start_simulation(_STUB)
        #gevent.sleep(5)
        #send_stock_selection(_STUB, "A005930")
        #gevent.joinall([gevent.spawn(tick_subscriber, _STUB), gevent.spawn(bidask_subscriber, _STUB), gevent.spawn(subject_subscriber, _STUB), gevent.spawn(time_listener, _STUB)])
    print('exit')

if __name__ == '__main__':
    run()
