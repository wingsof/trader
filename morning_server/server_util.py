from morning_server import stream_readwriter
from morning_server import message
from configs import db
from utils import time_converter

from pymongo import MongoClient
import gevent
from datetime import timedelta, datetime
from utils import logger


def stream_write(sock, header, body, manager = None):
    try:
        stream_readwriter.write(sock, header, body)
    except Exception as e:
        logger.error('Stream write error ' + str(e))
        if manager is not None:
            manager.handle_disconnect(e.args[1])


class _Collector:
    def __init__(self, index, sock, capability):
        self.index = index
        self.sock = sock
        self.capability = capability
        self.subscribe_code = []
        self.latest_request_process_time = datetime.now()
        self.request = {
            'pending': False,
            'id': None,
            'socket': None,
            'count': 0}

    def __repr__(self):
        return 'latest_process_time:' + str(self.latest_request_process_time) + '\t' + str(self.request)

    def request_id(self):
        return self.request['id']

    def request_pending(self):
        return self.request['pending']

    def request_socket(self):
        return self.request['socket']

    def subscribe_count(self):
        return len(self.subscribe_code)

    def set_pending(self, is_pending):
        #print('set_pending', is_pending)
        self.request['pending'] = is_pending
        if not is_pending:
            self.request['id'] = None

    def append_subscribe_code(self, code):
        self.subscribe_code.append(code)

    def set_request(self, sock, msg_id, is_pending):
        self.request['socket'] = sock
        self.request['id'] = msg_id
        self.set_pending(is_pending)


class CollectorList:
    def __init__(self):
        self.collectors = []
        self.collector_index = 0

    def add_collector(self, sock, body):
        self.collectors.append(_Collector(self.collector_index, sock, body['capability']))

    def handle_disconnect(self, sock):
        logger.warning('HANDLE DISCONNECT: CollectorList')
        collector = None
        for c in self.collectors:
            if c.sock == sock:
                logger.warning('Collector Removed')
                collector = c
                break

        if collector is not None:
            # TODO: Notify collector disconnected events to clients
            self.collectors.remove(collector)

    def get_available_trade_collector(self):
        while True:
            collector = self.find_trade_collector()
            if collector is not None:
                break
            gevent.sleep()
        return collector

    def get_available_request_collector(self):
        while True:
            collector = self.find_request_collector()
            if collector is not None:
                break
            gevent.sleep()
        return collector

    def find_by_id(self, msg_id):
        for c in self.collectors:
            if c.request_id() == msg_id:
                return c
        return None

    def find_request_collector(self):
        available_collectors = []
        for c in self.collectors:
            if c.capability & message.CAPABILITY_REQUEST_RESPONSE and not c.request_pending():
                available_collectors.append(c)

        if len(available_collectors) == 0:
            return None
        
        available_collectors = sorted(available_collectors, key=lambda x: x.latest_request_process_time)
        available_collectors[0].latest_request_process_time = datetime.now()
        return available_collectors[0]

    def find_subscribe_collector(self):
        collector = None
        for c in self.collectors:
            if c.capability & message.CAPABILITY_COLLECT_SUBSCRIBE and c.subscribe_count() < 400:
                if collector is None:
                    collector = c
                else:
                    if collector.subscribe_count() > c.subscribe_count():
                        collector = c
        return collector

    def find_trade_collector(self):
        collector = None
        for c in self.collectors:
            if c.capability & message.CAPABILITY_TRADE and not c.request_pending():
                collector = c
                break

        return collector


class SubscribeClient:
    def __init__(self):
        # Key: code, Values: (collector_socket, [subscribe_client_socket, ])
        self.clients = dict()
        self.trade_clients = []

    def code_in_clients(self, code):
        return code in self.clients

    def add_trade_to_clients(self, sock):
        if sock not in self.trade_clients:
            self.trade_clients.append(sock)

    def send_to_clients(self, code, header, body):
        if self.code_in_clients(code):
            #logger.info('Subscribe socket count %d', len(self.clients[code][1]))
            # STOP subscribe when client sock len is zero
            for s in self.clients[code][1]:
                stream_write(s, header, body, self)

    def send_trade_to_client(self, header, body):
        for s in self.trade_clients:
            stream_write(s, header, body, self)

    def handle_disconnect(self, sock):
        logger.warning('HANDLE DISCONNECT: SubscribeClient')
        for v in self.clients.values():
            for s in v[1]:
                if s == sock:
                    # Assume that sock is not duplicated in a code
                    v[1].remove(sock)
                    #break
        if sock in self.trade_clients:
            self.trade_clients.remove(sock)

        #TODO:stop subscribe when no client and decrement counts
        for k, v in self.clients.items():
            if len(v[1]) == 0:
                pass 


    def add_to_clients(self, code, sock, header, body, collectors):
        if self.code_in_clients(code):
            found = False
            for s in self.clients[code][1]:
                if s == sock:
                    found = True
                    break
            if not found:
                self.clients[code][1].append(sock)
        else:
            collector = collectors.find_subscribe_collector()
            if collector is None:
                logger.error('NO AVAILABLE Subscribe collector')
                # TODO return FULL
            else:
                collector.append_subscribe_code(code)
                self.clients[code] = (collector.sock, [sock])
                logger.info('ADD NEW SUBSCRIBE %s', code)
                stream_write(collector.sock, header, body, collectors)


class _Partial:
    def __init__(self, header, db_data, count):
        self.header = header
        self.count = count
        self.data = []
        self.db_data = db_data

    def add_body(self, body, header):
        self.data.append(body)

        if len(body) == 0:
            stock_db = MongoClient(db.HOME_MONGO_ADDRESS)['stock']
            code = db.tr_code(header['code'])
            from_date = header['from']
            until_date = header['until']
            while from_date <= until_date:
                stock_db[code + '_V'].insert_one({'0': time_converter.datetime_to_intdate(from_date)})
                from_date += timedelta(days=1)
            #print('RECORD DATA to DB as EMPTY', header['method'], header['code'], header['from'], header['until'])
        else:
            stock_db = MongoClient(db.HOME_MONGO_ADDRESS)['stock']
            code = db.tr_code(header['code'])
            if header['method'] == message.DAY_DATA:
                stock_db[code + '_D'].insert_many(body)
            elif header['method'] == message.MINUTE_DATA:
                stock_db[code + '_M'].insert_many(body)
            elif header['method'] == message.INVESTOR_DATA:
                stock_db[code + '_INVESTOR'].insert_many(body)
            
            #print('RECORD DATA to DB', header['method'], header['code'], header['from'], header['until'])

        return len(self.data) == self.count

    def get_whole_message(self):
        datas = []
        if len(self.db_data) > 0:
            datas.append(self.db_data)

        for d in self.data:
            if len(d) > 0:
                datas.append(d)

        if len(datas) == 0:
            return datas
        elif len(datas) == 1:
            return datas[0]

        dates = []
        for i, d in enumerate(datas): # TODO: check error when Key '0' not exist
            dates.append((i, d[0]['0']))

        dates = sorted(dates, key=lambda d: d[1])
        final_data = []
        for d in dates:
            final_data.extend(datas[d[0]])
        return final_data


class PartialRequest:
    def __init__(self):
        self.client = dict()

    def start_partial_request(self, header, data, count):
        self.client[header['_id']] = _Partial(header, data, count)

    def get_item(self, msg_id):
        if msg_id in self.client:
            return self.client[msg_id]

        return None

    def pop_item(self, msg_id):
        if msg_id in self.client:
            self.client.pop(msg_id, None)
