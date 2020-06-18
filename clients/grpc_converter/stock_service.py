from gevent import monkey
monkey.patch_all()

import grpc.experimental.gevent as grpc_gevent
grpc_gevent.init_gevent()

import grpc
import gevent

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))

from concurrent import futures
import stock_provider_pb2_grpc
import stock_provider_pb2

from datetime import datetime, timedelta
from clients.common import morning_client
from morning.back_data import holidays
from pymongo import MongoClient
from morning_server import stock_api
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.empty_pb2 import Empty
from gevent.queue import Queue


simulation_progressing = [False, False, False]
TIME_SPEED = 1


def get_yesterday_data(today, market_code):
    yesterday = holidays.get_yesterday(today)
    yesterday_list = []
    for progress, code in enumerate(market_code):
        print('collect yesterday data', f'{progress+1}/{len(market_code)}', end='\r')
        data = morning_client.get_past_day_data(code, yesterday, yesterday)
        if len(data) == 1:
            data = data[0]
            data['code'] = code
            yesterday_list.append(data)
    print('')
    return yesterday_list


def collect_db(db, from_time, until_time):
    collection_name = 'T' + from_time.strftime('%Y%m%d')
    return list(db[collection_name].find({'date': {'$gt': from_time, '$lte': until_time}}))


def deliver_tick(tick_queue, stock_tick_handler, bidask_tick_handler, subject_tick_handler, time_handler):
    global simulation_progressing

    simulation_progressing[2] = True
    while simulation_progressing[0]:
        try:
            data = tick_queue.get(True, 1)
        except gevent.queue.Empty as ge:
            print('deliver tick queue empty', simulation_progressing)
            continue

        print('put ticks', len(data))
        now = datetime.now()
        datatime = None
        timeadjust = timedelta(seconds=0)
        for d in data:
            if not simulation_progressing[0]:
                break

            if datatime is None:
                datatime = d['date'] - timedelta(seconds=1)
            
            while (d['date'] - datatime) * TIME_SPEED > datetime.now() - now:
                gevent.sleep()

            timeadjust = (datetime.now() - now) - (d['date'] - datatime) * TIME_SPEED

            if d['type'] == 'subject':
                subject_tick_handler(d['code'], [d])
            elif d['type'] == 'bidask':
                bidask_tick_handler(d['code'], [d])
            else:
                stock_tick_handler(d['code'], [d])

            datatime = d['date'] - timeadjust
            now = datetime.now()
            #time_handler(datatime)
    simulation_progressing[2] = False
    print('exit deliver tick')


def start_tick_provider(simulation_datetime, stock_tick_handler, bidask_tick_handler, subject_tick_handler, time_handler):
    global simulation_progressing
    AT_ONCE_SECONDS = 60
    tick_queue = Queue(3)
    db = MongoClient('mongodb://127.0.0.1:27017').trade_alarm
    finish_time = simulation_datetime.replace(hour=15, minute=30)
    simulation_progressing[1] = True

    gevent.spawn(deliver_tick, tick_queue, stock_tick_handler, bidask_tick_handler, subject_tick_handler, time_handler)
    while simulation_datetime <= finish_time and simulation_progressing[0]:
        print('load data', simulation_datetime, 'data period seconds', AT_ONCE_SECONDS, 'real time', datetime.now())
        data = collect_db(db, simulation_datetime, simulation_datetime + timedelta(seconds=AT_ONCE_SECONDS))

        while True:
            try:
                #print('Before put the data in the queue')
                tick_queue.put(data, True, 1)
                #print('After put the data in the queue')
                break
            except gevent.queue.Full as ge:
                #print('Queue Full', simulation_progressing)
                if not simulation_progressing[0]:
                    print('Queue Full and exit simulation')
                    break

        simulation_datetime += timedelta(seconds=AT_ONCE_SECONDS)
        gevent.sleep()
        print('load done', simulation_datetime, 'tick len', len(data), 'real time', datetime.now())
    simulation_progressing[1] = False


class StockServicer(stock_provider_pb2_grpc.StockServicer):
    def __init__(self):
        print('StockService init')
        self.stock_subscribe_clients = []
        self.bidask_subscribe_cilents = []
        self.subject_subscribe_clients = []
        self.current_time_subscribe_clients = []
        self.current_stock_selection_subscribe_clients = []
        self.current_stock_code = ""
        self.current_stock_count_of_days = 0
        self.current_stock_until_time = None

    def GetDayData(self, request, context):
        print('GetDayData', request.code, datetime.fromtimestamp(request.from_datetime.seconds), datetime.fromtimestamp(request.until_datetime.seconds))
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
                date = m['0'],
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

    def GetPastMinuteData(self, request, context):
        print('GetPastMinuteData', request)
        today = datetime.fromtimestamp(request.today.seconds)
        yesterday = holidays.get_yesterday(today)
        from_date = holidays.get_date_by_previous_working_day_count(yesterday, request.count_of_days - 1)
        print('GetPastMinuteData', from_date, yesterday)
        minute_datas = morning_client.get_minute_data(request.code, from_date, yesterday)
        protoc_converted = []
        for m in minute_datas:
            protoc_converted.append(stock_provider_pb2.CybosDayData(
                date = m['0'],
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

    def RequestCybosSubject(self, request, context):
        stock_api.subscribe_stock_subject(morning_client.get_reader(),
                                        request.code, self.handle_subject_tick) 
        print('Start Subscribe Subject', request.code)
        return Empty()

    def SetCurrentStock(self, request, context):
        self.current_stock_code = request.code
        self.current_stock_count_of_days = request.count_of_days
        self.current_stock_until_time = request.until_datetime

        for q in self.current_stock_selection_subscribe_clients:
            q.put_nowait((request.code, request.count_of_days, request.until_datetime))
        print('SetCurrentStock', request.code, request.count_of_days, request.until_datetime)
        return Empty()

    def handle_bidask_tick(self, code, data):
        if len(data) != 1:
            return
        
        if '_BA' in code:
            code = code[:code.index('_')]

        data = data[0]
        tick_date = Timestamp()
        tick_date.FromDatetime(data['date'])
        bidask = stock_provider_pb2.CybosBidAskTickData(tick_date=tick_date,
                                                    code=data['code'],
                                                    time=data['1'],
                                                    volume=data['2'],
                                                    total_ask_remain=data['23'],
                                                    total_bid_remain=data['24'],
                                                    out_time_total_ask_remain=data['25'],
                                                    out_time_total_bid_remain=data['26'])
        for i in range(3, 19+1, 4):
            bidask.ask_prices.append(data[str(i)])
            bidask.bid_prices.append(data[str(i+1)])
            bidask.ask_remains.append(data[str(i+2)])
            bidask.bid_remains.append(data[str(i+3)])

        for i in range(27, 43+1, 4):
            bidask.ask_prices.append(data[str(i)])
            bidask.bid_prices.append(data[str(i+1)])
            bidask.ask_remains.append(data[str(i+2)])
            bidask.bid_remains.append(data[str(i+3)])

        for q in self.bidask_subscribe_cilents:
            q.put_nowait(bidask)

    def handle_stock_tick(self, code, data):
        #print('handle_stock_stick', data)
        if len(data) != 1:
            return

        data = data[0]
        tick_date = Timestamp()
        tick_date.FromDatetime(data['date'])
        data = stock_provider_pb2.CybosTickData(tick_date=tick_date,
                                                code=data['code'],
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
                                                cum_buy_volume=data['28'],
                                                is_kospi=morning_client.is_kospi_code(code))
        for q in self.stock_subscribe_clients:
            q.put_nowait(data)

    def handle_subject_tick(self, code, data):
        if len(data) != 1:
            return

        data = data[0]
        tick_date = Timestamp()
        tick_date.FromDatetime(data['date'])
        data = stock_provider_pb2.CybosSubjectTickData(tick_date=tick_date,
                                                        time=data['0'],
                                                        name=data['1'],
                                                        code=data['code'],
                                                        company_name=data['3'],
                                                        buy_or_sell=(data['4'] == ord('2')),
                                                        volume=data['5'],
                                                        total_volume=data['6'],
                                                        foreigner_total_volume=data['8'])
        for q in self.subject_subscribe_clients:
            q.put_nowait(data)

    def ListenCurrentStock(self, request, context):
        print('Run Listen Current Stock', len(self.current_stock_selection_subscribe_clients))
        q = Queue()
        self.current_stock_selection_subscribe_clients.append(q)

        if len(self.current_stock_code) > 0:
            yield stock_provider_pb2.StockSelection(code=self.current_stock_code,
                                                    count_of_days=self.current_stock_count_of_days,
                                                    until_datetime=self.current_stock_until_time)

        while context.is_active():
            try:
                data = q.get(True, 1)
                yield stock_provider_pb2.StockSelection(code=data[0], count_of_days=data[1], until_datetime=data[2])
            except gevent.queue.Empty as ge:
                pass
        self.current_stock_selection_subscribe_clients.remove(q)
        print('Done ListenCurrentStock', len(self.current_stock_selection_subscribe_clients)) 

    def ListenCybosTickData(self, request, context):
        print('ListenCybosTickData', len(self.stock_subscribe_clients))
        q = Queue()
        self.stock_subscribe_clients.append(q)

        while context.is_active():
            try:
                data = q.get(True, 1)
                yield data
            except gevent.queue.Empty as ge:
                pass
        self.stock_subscribe_clients.remove(q)
        print('Done SubscribeStock', len(self.stock_subscribe_clients))

    def ListenCybosBidAsk(self, request, context):
        print('ListenCybosBidAsk', len(self.bidask_subscribe_cilents))
        q = Queue()
        self.bidask_subscribe_cilents.append(q)

        while context.is_active():
            try:
                data = q.get(True, 1)
                yield data
            except gevent.queue.Empty as ge:
                pass

        self.bidask_subscribe_cilents.remove(q)
        print('Done SubscribeBidAsk', len(self.bidask_subscribe_cilents))

    def ListenCybosSubject(self, request, context):
        print('ListenCybosSubject', len(self.subject_subscribe_clients))
        q = Queue()
        self.subject_subscribe_clients.append(q)
        while context.is_active():
            try:
                data = q.get(True, 1)
                yield data
            except gevent.queue.Empty as ge:
                pass
        
        self.subject_subscribe_clients.remove(q)
        print('Done ListenCybosSubject', len(self.subject_subscribe_clients))

    def handle_time(self, d):
        data_date = Timestamp()
        data_date.FromDatetime(d)
        for q in self.current_time_subscribe_clients:
            q.put(data_date)

    def ListenCurrentTime(self, request, context):
        print('ListenCurrentTime', len(self.current_time_subscribe_clients))
        q = Queue()
        self.current_time_subscribe_clients.append(q)

        while context.is_active():
            try:
                data = q.get(True, 1)
                yield data
            except gevent.queue.Empty as ge:
                pass

        self.current_time_subscribe_clients.remove(q)
        print('Done ListenCurrentTime', len(self.current_time_subscribe_clients))

    def GetYesterdayTopAmountCodes(self, request, context):
        market_code = morning_client.get_all_market_code()
        request_date = request.toDateTime()
        print('GetYesterdayTopAmountCodes', request_date)
        yesterday_list = get_yesterday_data(request_date, market_code)
        yesterday_list = sorted(yesterday_list, key=lambda x: x['amount'], reverse=True)
        yesterday_list = yesterday_list[:1000]
        market_codes = [yl['code'] for yl in yesterday_list]
        print('Done GetYesterdayTopAmountCodes')
        return stock_provider_pb2.CodeList(codelist=market_codes)

    def StartSimulation(self, request, context):
        global simulation_progressing
        triggered = False

        if not any(simulation_progressing):
            simulation_progressing[0] = True
            triggered = True
            simulation_datetime = request.from_datetime.ToDatetime()
            gevent.spawn(start_tick_provider, simulation_datetime, self.handle_stock_tick, self.handle_bidask_tick, self.handle_subject_tick, self.handle_time)
            print('Start Simulation Mode', simulation_datetime)
            while context.is_active():
                gevent.sleep(1)

        if triggered:
            simulation_progressing[0] = False
            print('Stop Simulation Mode')
        yield Empty()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    stock_provider_pb2_grpc.add_StockServicer_to_server(StockServicer(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
