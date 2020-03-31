from gevent import monkey
monkey.patch_all()

import grpc
import grpc.experimental.gevent as grpc_gevent
grpc_gevent.init_gevent()


import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))

from concurrent import futures
import stock_provider_pb2_grpc
import stock_provider_pb2

from datetime import datetime
from clients.common import morning_client
from morning_server import stock_api
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.empty_pb2 import Empty
from gevent.queue import Queue



class StockServicer(stock_provider_pb2_grpc.StockServicer):
    def __init__(self):
        self.stock_subscribe_queue = Queue()
        self.bidask_subscribe_queue = Queue()

    def GetDayData(self, request, context):
        print('GetDayData', request)
        day_datas = morning_client.get_past_day_data(
            request.code,
            datetime.fromtimestamp(request.from_datetime.seconds),
            datetime.fromtimestamp(request.until_datetime.seconds))
        protoc_converted = []
        for d in day_datas:
            protoc_converted.append(stock_provider_pb2.CybosDayData(
                date = d['0'],
                time = d['time'],
                start_price = d['start_price'],
                highest_price = d['highest_price'],
                lowest_price = d['lowest_price'],
                close_price = d['close_price'],
                volume = d['volume'],
                amount = d['amount'],
                cum_sell_volume = d['cum_sell_volume'],
                cum_buy_volume = d['cum_buy_volume'],
                foreigner_hold_volume = d['foreigner_hold_volume'],
                foreigner_hold_rate = d['foreigner_hold_rate'],
                institution_buy_volume = d['institution_buy_volume'],
                institution_cum_buy_volume = d['institution_cum_buy_volume']))

        return stock_provider_pb2.CybosDayDatas(day_data=protoc_converted)

    def GetMinuteData(self, request, context):
        print('GetMinuteData', request)
        minute_datas = morning_client.get_minute_data(
            request.code,
            datetime.fromtimestamp(request.from_datetime.seconds),
            datetime.fromtimestamp(request.until_datetime.seconds))
        protoc_converted = []
        for m in minute_datas:
            protoc_converted.append(stock_provider_pb2.CybosDayData(
                time = m['time'],
                start_price = m['start_price'],
                highest_price = m['highest_price'],
                lowest_price = m['lowest_price'],
                close_price = m['close_price'],
                volume = m['volume'],
                amount = m['amount'],
                cum_sell_volume = m['cum_sell_volume'],
                cum_buy_volume = m['cum_buy_volume'],
                foreigner_hold_volume = m['foreigner_hold_volume'],
                foreigner_hold_rate = m['foreigner_hold_rate'],
                institution_buy_volume = m['institution_buy_volume'],
                institution_cum_buy_volume = m['institution_cum_buy_volume']))

        return stock_provider_pb2.CybosDayDatas(day_data=protoc_converted)


    def RequestCybosTickData(self, request, context):
        stock_api.subscribe_stock(morning_client.get_reader(),
                                request.code, self.handle_stock_tick)
        print('Start SubscribeStock', request.code)
        return Empty()

    def RequestCybosBidAsk(self, request, context):
        stock_api.subscribe_stock_bidask(morning_client.get_reader(),
                                        request.code, self.handle_bidask_tick)
        print('Start Subscribe BidAsk', request.code)
        return Empty()

    def handle_bidask_tick(self, code, data):
        if len(data) != 1:
            return
        
        code = code[:code.index('_')]

        data = data[0]
        tick_date = Timestamp()
        tick_date = tick_date.FromMilliseconds(int(datetime.timestamp(data['date']) * 1000))
        data = stock_provider_pb2.CybosBidAskTickData(tick_date=tick_date,
                                                    code=data['0'],
                                                    time=data['1'],
                                                    volume=data['2'],
                                                    first_ask_price=data['3'],
                                                    first_bid_price=data['4'],
                                                    first_ask_remain=data['5'],
                                                    first_bid_remain=data['6'],
                                                    second_ask_price=data['7'],
                                                    second_bid_price=data['8'],
                                                    second_ask_remain=data['9'],
                                                    second_bid_remain=data['10'],
                                                    third_ask_price=data['11'],
                                                    third_bid_price=data['12'],
                                                    third_ask_remain=data['13'],
                                                    third_bid_remain=data['14'],
                                                    fourth_ask_price=data['15'],
                                                    fourth_bid_price=data['16'],
                                                    fourth_ask_remain=data['17'],
                                                    fourth_bid_remain=data['18'],
                                                    fifth_ask_price=data['19'],
                                                    fifth_bid_price=data['20'],
                                                    fifth_ask_remain=data['21'],
                                                    fifth_bid_remain=data['22'],
                                                    total_ask_remain=data['23'],
                                                    total_bid_remain=data['24'],
                                                    out_time_total_ask_remain=data['25'],
                                                    out_time_total_bid_remain=data['26'])
        self.bidask_subscribe_queue.put(data)

    def handle_stock_tick(self, code, data):
        if len(data) != 1:
            return

        data = data[0]
        tick_date = Timestamp()
        tick_date = tick_date.FromMilliseconds(int(datetime.timestamp(data['date']) * 1000))
        data = stock_provider_pb2.CybosTickData(tick_date=tick_date,
                                                code=data['0'],
                                                company_name=data['1'],
                                                yesterday_diff=data['2'],
                                                time=data['3'],
                                                start_price=data['4'],
                                                highest_price=data['5'],
                                                lowest_price=data['6'],
                                                ask_price=data['7'],
                                                bid_price=data['8'],
                                                cum_volume=data['9'],
                                                cum_amount=data['10'],
                                                current_price=data['13'],
                                                buy_or_sell=(data['14'] == ord('1')),
                                                cum_sell_volume_by_price=data['15'],
                                                cum_buy_volume_by_price=data['16'],
                                                volume=data['17'],
                                                time_with_sec=data['18'],
                                                market_type_exp=data['19'],
                                                market_type=data['20'],
                                                out_time_volume=data['21'],
                                                cum_sell_volume=data['27'],
                                                cum_buy_volume=data['28'])
        self.stock_subscribe_queue.put(data)

    def ListenCybosTickData(self, request, context):
        print('ListenCybosTickData')
        while True:
            data = self.stock_subscribe_queue.get()
            print('delivered')
            yield data
        print('Done SubscribeStock')

    def ListenCybosBidAsk(self, request, context):
        print('ListenCybosBidAsk')
        while True:
            data = self.bidask_subscribe_queue.get()
            yield data
        print('Done SubscribeBidAsk')


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    stock_provider_pb2_grpc.add_StockServicer_to_server(StockServicer(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()