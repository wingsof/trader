from gevent import monkey
monkey.patch_all()

import grpc.experimental.gevent as grpc_gevent
grpc_gevent.init_gevent()

import grpc
import gevent

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))
import gc

import preload
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
from candidate import favorite
import todaydata
import config


simulation_progressing = [False, False, False]
request_stop_simulation = False
recent_search_codes = []
TIME_SPEED = 1.0
is_subscribe_alarm = False
is_subscribe_trade = False
is_subscribe_tick = {}
is_subscribe_bidask = {}
is_subscribe_subject = {}


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


def deliver_tick(tick_queue, stock_tick_handler, bidask_tick_handler, subject_tick_handler, alarm_tick_handler,
                        time_handler, simulation_handler):
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
        last_datatime = None
        timeadjust = timedelta(seconds=0)
        for d in data:
            if not simulation_progressing[0]:
                break
            
            if datatime is None:
                datatime = d['date'] - timedelta(seconds=1)
                last_datatime = datatime
            
            # TIME_SPEED greater, then tick deliver speed will be more slow

            while (d['date'] - datatime) * TIME_SPEED > datetime.now() - now:
                gevent.sleep()

            timeadjust = (datetime.now() - now) - (d['date'] - datatime) * TIME_SPEED
            d_date = d['date']

            if d['type'] == 'subject':
                subject_tick_handler(d['code'], [d])
            elif d['type'] == 'bidask':
                bidask_tick_handler(d['code'], [d])
            elif d['type'] == 'tick':
                stock_tick_handler(d['code'], [d])
            elif d['type'] == 'alarm':
                alarm_tick_handler(d['code'], [d])
            else:
                continue

            if d_date - last_datatime > timedelta(seconds=1):
                time_handler(d_date - timedelta(hours=9))    # DB time is UTC but time is set as if localtime
                last_datatime = d_date

            datatime = d_date - timeadjust
            now = datetime.now()
        
    simulation_progressing[2] = False
    if not any(simulation_progressing):
        simulation_handler([False])

    print('exit deliver tick')


def start_tick_provider(simulation_datetime, stock_tick_handler, bidask_tick_handler, subject_tick_handler, alarm_tick_handler, 
                            time_handler, simulation_handler):
    global simulation_progressing
    AT_ONCE_SECONDS = 60
    tick_queue = Queue(3)
    db = MongoClient('mongodb://127.0.0.1:27017').trade_alarm
    finish_time = simulation_datetime.replace(hour=15, minute=30)
    simulation_progressing[1] = True

    gevent.spawn(deliver_tick, tick_queue, stock_tick_handler, bidask_tick_handler, subject_tick_handler, alarm_tick_handler,
                        time_handler, simulation_handler)
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
    if not any(simulation_progressing):
        simulation_handler([False])


class StockServicer(stock_provider_pb2_grpc.StockServicer):
    def __init__(self, is_skip_ydata):
        print('StockService init start')
        self.skip_ydata = is_skip_ydata
        self.stock_subscribe_clients = []
        self.bidask_subscribe_cilents = []
        self.subject_subscribe_clients = []
        self.current_time_subscribe_clients = []
        self.alarm_subscribe_clients = []
        self.list_changed_subscribe_clients = []
        self.current_stock_selection_subscribe_clients = []
        self.simulation_changed_subscribe_clients = []
        self.order_result_subscribe_clients  = []
        self.cybos_order_result_subscribe_clients = []
        self.trader_clients = []
        self.current_stock_code = ""
        self.current_datetime = None
        preload.load(datetime.now(), self.skip_ydata)
        print('StockService init ready')

    def GetDayData(self, request, context):
        print('GetDayData', request.code,
                            request.from_datetime.ToDatetime() + timedelta(hours=9),
                            request.until_datetime.ToDatetime() + timedelta(hours=9))
        day_datas = morning_client.get_past_day_data(
            request.code,
            request.from_datetime.ToDatetime() + timedelta(hours=9),
            request.until_datetime.ToDatetime() + timedelta(hours=9))
        protoc_converted = []
        for d in day_datas:
            protoc_converted.append(stock_provider_pb2.CybosDayData(
                date = d['0'],
                time = d['time'],
                start_price = int(d['start_price']),
                highest_price = int(d['highest_price']),
                lowest_price = int(d['lowest_price']),
                close_price = int(d['close_price']),
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
        print('GetMinuteData', request.code,
                               request.from_datetime.ToDatetime() + timedelta(hours=9),
                               request.until_datetime.ToDatetime() + timedelta(hours=9))
        minute_datas = morning_client.get_minute_data(
            request.code,
            request.from_datetime.ToDatetime() + timedelta(hours=9),
            request.until_datetime.ToDatetime() + timedelta(hours=9))
        protoc_converted = []
        for m in minute_datas:
            protoc_converted.append(stock_provider_pb2.CybosDayData(
                date = m['0'],
                time = m['time'],
                start_price = int(m['start_price']),
                highest_price = int(m['highest_price']),
                lowest_price = int(m['lowest_price']),
                close_price = int(m['close_price']),
                volume = m['volume'],
                amount = m['amount'],
                cum_sell_volume = m['cum_sell_volume'],
                cum_buy_volume = m['cum_buy_volume'],
                foreigner_hold_volume = m['foreigner_hold_volume'],
                foreigner_hold_rate = m['foreigner_hold_rate'],
                institution_buy_volume = m['institution_buy_volume'],
                institution_cum_buy_volume = m['institution_cum_buy_volume']))

        return stock_provider_pb2.CybosDayDatas(day_data=protoc_converted)

    def GetTodayMinuteData(self, request, context):
        print("GetTodayMinuteData", request)
        minute_datas = morning_client.get_today_minute_data(request.code)
        protoc_converted = []
        for m in minute_datas:
            protoc_converted.append(stock_provider_pb2.CybosDayData(
                date = m['0'],
                time = m['time'],
                start_price = int(m['start_price']),
                highest_price = int(m['highest_price']),
                lowest_price = int(m['lowest_price']),
                close_price = int(m['close_price']),
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
        today = request.today.ToDatetime()
        yesterday = holidays.get_yesterday(today)
        from_date = holidays.get_date_by_previous_working_day_count(yesterday, request.count_of_days - 1)
        minute_datas = morning_client.get_minute_data(request.code, from_date, yesterday)
        protoc_converted = []
        for m in minute_datas:
            protoc_converted.append(stock_provider_pb2.CybosDayData(
                date = m['0'],
                time = m['time'],
                start_price = int(m['start_price']),
                highest_price = int(m['highest_price']),
                lowest_price = int(m['lowest_price']),
                close_price = int(m['close_price']),
                volume = m['volume'],
                amount = m['amount'],
                cum_sell_volume = m['cum_sell_volume'],
                cum_buy_volume = m['cum_buy_volume'],
                foreigner_hold_volume = m['foreigner_hold_volume'],
                foreigner_hold_rate = m['foreigner_hold_rate'],
                institution_buy_volume = m['institution_buy_volume'],
                institution_cum_buy_volume = m['institution_cum_buy_volume']))

        return stock_provider_pb2.CybosDayDatas(day_data=protoc_converted)
      
    def IsKospi(self, request, context):
        return stock_provider_pb2.Bool(ret=preload.is_kospi(request.code))

    def GetCompanyName(self, request, context):
        return stock_provider_pb2.CompanyName(company_name=preload.get_corp_name(request.code))

    def GetSubscribeCodes(self, request, context):
        codes_filtered = []
        codes = morning_client.get_subscribe_codes()
        for code in codes:
            if (code.startswith('A') or code.startswith('U')) and len(code) <= 7:
                codes_filtered.append(code)
        return stock_provider_pb2.CodeList(codelist=codes_filtered)

    def ReportOrderResult(self, request, context):
        for o in self.order_result_subscribe_clients:
            o.put_nowait(request)
        return Empty()

    def RequestCybosTickData(self, request, context):
        global is_subscribe_tick
        if request.code not in is_subscribe_tick:
            stock_api.subscribe_stock(morning_client.get_reader(),
                                    request.code, self.handle_stock_tick)
            print('Start SubscribeStock', request.code)
            is_subscribe_tick[request.code] = True
        else:
            print('Already SubscribeStock', request.code)
        return Empty()

    def RequestCybosBidAsk(self, request, context):
        global is_subscribe_bidask
        if request.code not in is_subscribe_bidask:
            stock_api.subscribe_stock_bidask(morning_client.get_reader(),
                                            request.code, self.handle_bidask_tick)
            print('Start Subscribe BidAsk', request.code)
            is_subscribe_bidask[request.code] = True
        else:
            print('Already Subscribe BidAsk', request.code)
        return Empty()

    def RequestCybosSubject(self, request, context):
        global is_subscribe_subject
        if request.code not in is_subscribe_subject:
            stock_api.subscribe_stock_subject(morning_client.get_reader(),
                                            request.code, self.handle_subject_tick) 
            print('Start Subscribe Subject', request.code)
            is_subscribe_subject[request.code] = True
        else:
            print('Already Subscribe Subject', request.code)
        return Empty()

    def RequestCybosAlarm(self, request, context):
        global is_subscribe_alarm

        if not is_subscribe_alarm:
            stock_api.subscribe_alarm(morning_client.get_reader(),
                                        self.handle_alarm_tick)
            print('Start Subscribe alarm')
            is_subscribe_alarm = True
        else:
            print('Already subscribe alarm')
        return Empty()

    def RequestCybosTradeResult(self, request, context):
        global is_subscribe_trade

        if not is_subscribe_trade:
            print('Start Trade Result')
            stock_api.subscribe_trade(morning_client.get_reader(),
                                        self.handle_trade_result)
            is_subscribe_trade = True
        else:
            print('Already subscribe trade')
        return Empty()

    def GetBalance(self, request, context):
        balance = morning_client.get_balance()
        return stock_provider_pb2.Balance(balance=balance)

    def ClearRecentList(self, request, context):
        if len(recent_search_codes) > 0:
            recent_search_codes.clear()
            self.send_list_changed('recent')

    def send_list_changed(self, type_name):
        for c in self.list_changed_subscribe_clients:
            c.put_nowait(stock_provider_pb2.ListType(type_name=type_name))

    def RequestToTrader(self, request, context):
        for o in self.trader_clients:
            o.put_nowait(request)
        return Empty()

    def GetViPrice(self, request, context):
        return stock_provider_pb2.Prices(price=todaydata.get_vi_prices(request.code))

    def SetCurrentStock(self, request, context):
        global recent_search_codes
        if len(request.code) == 0:
            return Empty()

        self.current_stock_code = request.code

        for q in self.current_stock_selection_subscribe_clients:
            q.put_nowait(stock_provider_pb2.StockCodeQuery(code=request.code))

        if request.code not in recent_search_codes: # TODO: when code is selected in recent list then?
            recent_search_codes.insert(0, request.code)
            self.send_list_changed('recent')

        print('SetCurrentStock', request.code())
        return Empty()

    def SetCurrentDateTime(self, request ,context):
        print('SetCurrentDateTime : ', request.ToDatetime())
        todaydata.clear_all()

        preload.load(request.ToDatetime() + timedelta(hours=9), self.skip_ydata)
        self.handle_time(request.ToDatetime())
        return Empty()

    def AddFavorite(self, request, context):
        print('AddFavorite', request.code)
        if favorite.add_to_favorite(request.code):
            self.send_list_changed('favorite')
        return Empty()

    def RemoveFavorite(self, request, context):
        print('RemoveFavorite', request.code)
        if favorite.remove_from_favorite(request.code):
            self.send_list_changed('favorite')
        return Empty()

    def GetViList(self, request, context):
        print('GetViList', request.type)
        return stock_provider_pb2.CodeList(codelist=todaydata.get_vi(request.type, request.catch_plus))

    def GetTodayTopAmountList(self, request, context):
        print('GetTodayTopAmountList')
        return stock_provider_pb2.CodeList(codelist=todaydata.get_today_list(request.type, request.catch_plus, request.use_accumulated))


    def GetTodayNineThirtyList(self, request, context):
        print('GetTodayNineThirtyList')
        return stock_provider_pb2.CodeList(codelist=todaydata.get_ninethirty_list())


    def SetSimulationStatus(self, request, context):
        global TIME_SPEED
        TIME_SPEED = request.simulation_speed
        return Empty()


    def GetSimulationStatus(self, request, context):
        is_simulation = any(simulation_progressing)
        return stock_provider_pb2.SimulationStatus(simulation_on=is_simulation,
                                                    simulation_speed=TIME_SPEED)

    def handle_bidask_tick(self, code, data_arr):
        if len(data_arr) != 1:
            return

        if '_BA' in code:
            code = code[:code.index('_')]

        data = data_arr[0]
        tick_date = Timestamp()
        tick_date.FromDatetime(data['date'])
        bidask = stock_provider_pb2.CybosBidAskTickData(tick_date=tick_date,
                                                    code=code,
                                                    time=data['1'],
                                                    volume=data['2'],
                                                    total_ask_remain=data['23'],
                                                    total_bid_remain=data['24'],
                                                    out_time_total_ask_remain=data['25'],
                                                    out_time_total_bid_remain=data['26'])
        for i in range(3, 19+1, 4):
            if data[str(i+1)] > 0:
                bidask.bid_prices.append(data[str(i+1)])
                bidask.bid_remains.append(data[str(i+3)])

            if data[str(i)] > 0:
                bidask.ask_prices.append(data[str(i)])
                bidask.ask_remains.append(data[str(i+2)])

        for i in range(27, 43+1, 4):
            if data[str(i+1)] > 0:
                bidask.bid_prices.append(data[str(i+1)])
                bidask.bid_remains.append(data[str(i+3)])

            if data[str(i)] > 0:
                bidask.ask_prices.append(data[str(i)])
                bidask.ask_remains.append(data[str(i+2)])

        for q in self.bidask_subscribe_cilents:
            q.put_nowait(bidask)

        #gevent.sleep(0.0001)

    def handle_stock_tick(self, code, data_arr):
        #print('handle_stock_stick', data)
        if len(data_arr) != 1:
            return

        data = data_arr[0]
        tick_date = Timestamp()
        tick_date.FromDatetime(data['date'] - timedelta(hours=9))

        ret = todaydata.handle_today_tick(code, data)
        if ret & config.CAND_TODAY_BUL:
            self.send_list_changed('ttopamount')
        if ret & config.CAND_NINETHIRTY:
            self.send_list_changed('ninethirty')
        tick_data = stock_provider_pb2.CybosTickData(tick_date=tick_date,
                                                code=code,
                                                company_name=data['1'],
                                                yesterday_diff=data['2'],
                                                time=data['3'],
                                                start_price=int(data['4']),
                                                highest_price=int(data['5']),
                                                lowest_price=int(data['6']),
                                                ask_price=int(data['7']),
                                                bid_price=int(data['8']),
                                                cum_volume=data['9'],
                                                cum_amount=data['10'],
                                                current_price=int(data['13']),
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
            q.put_nowait(tick_data)
        #gevent.sleep(0.0001)

    def handle_subject_tick(self, code, data_arr):
        if len(data_arr) != 1:
            return

        if '_' in code:
            code = code[:code.index('_')]

        data = data_arr[0]

        tick_date = Timestamp()
        tick_date.FromDatetime(data['date'] - timedelta(hours=9))
        tick_data = stock_provider_pb2.CybosSubjectTickData(tick_date=tick_date,
                                                        time=data['0'],
                                                        name=data['1'],
                                                        code=code,
                                                        company_name=data['3'],
                                                        buy_or_sell=(data['4'] == ord('2')),
                                                        volume=data['5'],
                                                        total_volume=data['6'],
                                                        foreigner_total_volume=data['8'])

        for q in self.subject_subscribe_clients:
            q.put_nowait(tick_data)
        gevent.sleep(0.000001)

    def handle_alarm_tick(self, _, data_arr):
        if len(data_arr) != 1:
            return

        data = data_arr[0]
        tick_date = Timestamp()
        tick_date.FromDatetime(data['date'] - timedelta(hours=9))
        code = data['code'] if 'code' in data else data['3']
        if todaydata.handle_vi(code, data):
            self.send_list_changed('vi')

        tick_data = stock_provider_pb2.CybosStockAlarm(tick_date=tick_date,
                                                time=data['0'],
                                                type_category=data['1'],
                                                market_category=data['2'],
                                                code=code,
                                                alarm_category=data['4'],
                                                title=data['5'],
                                                content=data['6'])
        for q in self.alarm_subscribe_clients:
            q.put_nowait(tick_data)

        gevent.sleep(0.000001)

    def handle_trade_result(self, data):
        """
        result = {
            'flag': flag,
            'code': code,
            'order_number': order_num,
            'quantity': quantity,
            'price': price,
            'order_type': order_type,
            'total_quantity': total_quantity
        }
        """
        if 'flag' not in data or 'quantity' not in data or 'code' not in data:
            print('RESULT without flag or quantity %s', str(data))
        else:
            data = stock_provider_pb2.CybosOrderResult(flag=ord(data['flag']),
                                                        code=data['code'],
                                                        order_number=str(data['order_number']),
                                                        price=data['price'],
                                                        is_buy=(data['order_type'] == '2'),
                                                        quantity=data['quantity'],
                                                        total_quantity=data['total_quantity'])
            print(data)
            for q in self.cybos_order_result_subscribe_clients:
                q.put_nowait(data)

    def handle_time(self, d):
        self.current_datetime = d
        data_date = Timestamp()
        data_date.FromDatetime(d)
        for q in self.current_time_subscribe_clients:
            q.put(data_date)

    def handle_simulation(self, d):
        for q in self.simulation_changed_subscribe_clients:
            print('handle_simulation', d[0])
            q.put(stock_provider_pb2.SimulationStatus(simulation_on=d[0], simulation_speed=TIME_SPEED))

    def ListenCurrentTime(self, request, context):
        title = 'ListenCurrentTime' 
        client_list = self.current_time_subscribe_clients
        q = Queue()
        client_list.append(q)
        print(title, len(client_list))

        current = Timestamp()
        if self.current_datetime is None:
            current.FromDatetime(datetime.now() - timedelta(hours=9))
        else:
            current.FromDatetime(self.current_datetime)

        yield current

        while context.is_active():
            try:
                data = q.get(True, 1)
                yield data
            except gevent.queue.Empty as ge:
                pass
        client_list.remove(q)
        print('Done', title, len(client_list))

    def handle_queue_based_listener(self, title, client_list, context):
        q = Queue()
        client_list.append(q)
        print(title, len(client_list))
        while context.is_active():
            try:
                data = q.get(True, 1)
                yield data
            except gevent.queue.Empty as ge:
                pass
        client_list.remove(q)
        print('Done', title, len(client_list))

    def ListenCurrentStock(self, request, context):
        if len(self.current_stock_code) > 0:
            yield stock_provider_pb2.StockCodeQuery(code=self.current_stock_code)

        data = self.handle_queue_based_listener('ListenCurrentStock',
                                                self.current_stock_selection_subscribe_clients,
                                                context)
        for d in data:
            yield d

    def ListenListChanged(self, request, context):
        data = self.handle_queue_based_listener('ListenListChanged',
                                                self.list_changed_subscribe_clients,
                                                context)
        for d in data:
            yield d

    def ListenCybosTickData(self, request, context):
        data = self.handle_queue_based_listener('ListenCybosTickData',
                                                self.stock_subscribe_clients,
                                                context)
        for d in data:
            yield d

    def ListenCybosBidAsk(self, request, context):
        data = self.handle_queue_based_listener('ListenCybosBidAsk',
                                                self.bidask_subscribe_cilents,
                                                context)
        for d in data:
            yield d


    def ListenCybosSubject(self, request, context):
        data = self.handle_queue_based_listener('ListenCybosSubject',
                                                self.subject_subscribe_clients,
                                                context)
        for d in data:
            yield d

    def ListenCybosAlarm(self, request, context):
        data = self.handle_queue_based_listener('ListenCybosAlarm',
                                                self.alarm_subscribe_clients,
                                                context)
        for d in data:
            yield d

    def ListenOrderResult(self, request, context):
        data = self.handle_queue_based_listener('ListenOrderResult',
                                                self.order_result_subscribe_clients,
                                                context)
        for d in data:
            yield d

    def ListenCybosOrderResult(self, request, context):
        data = self.handle_queue_based_listener('ListenCybosOrderResult',
                                                self.cybos_order_result_subscribe_clients,
                                                context)
        for d in data:
            yield d

    def ListenSimulationStatusChanged(self, request, context):
        data = self.handle_queue_based_listener('ListenSimulationStatusChanged',
                                                self.simulation_changed_subscribe_clients,
                                                context)
        for d in data:
            yield d

    def ListenTraderMsg(self, request, context):
        data = self.handle_queue_based_listener('ListenTraderMsg',
                                                self.trader_clients,
                                                context)
        for d in data:
            yield d

    def GetRecentSearch(self, request, context):
        return stock_provider_pb2.CodeList(codelist=recent_search_codes)

    def GetFavoriteList(self, request, context):
        return stock_provider_pb2.CodeList(codelist=favorite.get_favorite())

    def GetYesterdayTopAmountList(self, request, context):
        dt = request.ToDatetime() + timedelta(hours=9)
        top_list = morning_client.get_yesterday_top_amount(dt) 
        print('GetYesterdayTopAmountList', dt, 'count : ', len(top_list[0]), top_list[1], top_list[2])
        return stock_provider_pb2.TopList(codelist=top_list[0], is_today_data=top_list[1], date=top_list[2])

    def OrderStock(self, request, context):
        ret = stock_api.order_stock(morning_client.get_reader(), request.code, request.price, request.quantity, request.is_buy)
        print('OrderStock', request, ret)
        return stock_provider_pb2.CybosOrderReturn(result=ret['status'], msg=ret['msg'])

    def ChangeOrder(self, request, context):
        try:
            order_num = int(request.order_num)
            ret = stock_api.modify_order(morning_client.get_reader(), order_num, request.code, request.price)
            print('ChangeOrder', request, ret)
        except ValueError as ve:
            print('ValueError', ve)
            return stock_provider_pb2.CybosOrderReturn(order_num=0, msg='Value Error ' + str(request.order_num))

        return stock_provider_pb2.CybosOrderReturn(order_num=ret['order_number'])

    def CancelOrder(self, request, context):
        try:
            order_num = int(request.order_num)
            ret = stock_api.cancel_order(morning_client.get_reader(), order_num, request.code, request.quantity)
            print('CancelOrder', request, ret)
        except ValueError as ve:
            print('ValueError', ve)
            return stock_provider_pb2.CybosOrderReturn(result=['result'], msg='Value Error ' + request.order_num)

        return stock_provider_pb2.CybosOrderReturn(result=ret['result'])

    def StartSimulation(self, request, context):
        global simulation_progressing, request_stop_simulation
        if preload.loading:
            print('Preloading data, cannot start simulation')
            yield Empty()
            return

        triggered = False

        if not any(simulation_progressing):
            simulation_progressing[0] = True
            triggered = True

            todaydata.clear_all()
            if self.current_datetime is not None:
                gevent.spawn(start_tick_provider, self.current_datetime + timedelta(hours=9), self.handle_stock_tick, self.handle_bidask_tick, self.handle_subject_tick, self.handle_alarm_tick, self.handle_time, self.handle_simulation)

            self.handle_simulation([True])
            print('Start Simulation Mode', self.current_datetime + timedelta(hours=9))
            while context.is_active() and not request_stop_simulation:
                gevent.sleep(1)

        if triggered:
            request_stop_simulation = False
            simulation_progressing[0] = False
            print('Stop Simulation Mode')
        
        yield Empty()

    def StopSimulation(self, request, context):
        print('StopSimulation')
        global request_stop_simulation
        if all(simulation_progressing):
            request_stop_simulation = True

        return Empty()


def serve():
    skip_ydata_loading = False
    if len(sys.argv) > 1 and sys.argv[1] == 'skip':
        skip_ydata_loading = True

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=60))
    stock_provider_pb2_grpc.add_StockServicer_to_server(StockServicer(skip_ydata_loading), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
