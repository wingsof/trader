from datetime import datetime

from morning_server import message
from morning_server.server_util import stream_write
from utils import logger
import gevent


class _Collector:
    def __init__(self, sock, capability, vendor):
        self.sock = sock
        self.capability = capability
        self.vendor = vendor
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

    def get_vendor(self):
        return self.vendor

    def set_pending(self, is_pending):
        #print('set_pending', is_pending)
        self.request['pending'] = is_pending
        if not is_pending:
            self.request['id'] = None

    def append_subscribe_code(self, code):
        self.subscribe_code.append(code)

    def remove_subscribe_code(self, code):
        self.subscribe_code.remove(code)

    def set_request(self, sock, msg_id, is_pending):
        self.request['socket'] = sock
        self.request['id'] = msg_id
        self.set_pending(is_pending)



class ClientManager:
    def __init__(self):
        self.collectors = []
        self.code_subscribe_info = dict()
        vendors = [message.CYBOS, message.KIWOOM]
        self.trade_subscribe_sockets = dict()
        for v in vendors:
            self.trade_subscribe_sockets[v] = []

    def handle_disconnect(self, sock):
        # TODO: identify whether sock is collector or client
        # 1. collector
        #   1-1. remove from self.collectors
        #   1-2. find collector in self.code_subscribe_info 
        #   1-3. find collector in trade
        # 2. client
        #   2-1. check trade client
        #   2-2. check code_subscribe_info
        pass

    def add_collector(self, sock, header, body):
        self.collectors.append(_Collector(sock, body['capability'], header['vendor']))

    def get_vendor_collector(self, vendor):
        collectors = []
        for c in self.collectors:
            if c.get_vendor() == vendor:
                collectors.append(c)
        return collectors

    def _get_collector(self, capability, vendor):
        for c in self.get_vendor_collector(vendor):
            if c.capability & capability:
                return c
        return None

    def _get_available_collector(self, capability, vendor):
        collector = None
        while True:
            for c in self.get_vendor_collector(vendor):
                if c.capability & capability and not c.request_pending():
                    collector = c
            if collector is not None:
                break
            gevent.sleep()
        return collector

    def get_available_trade_collector(self, vendor=message.CYBOS):
        return self._get_available_collector(message.CAPABILITY_TRADE, vendor)

    def get_trade_collector(self, vendor=message.CYBOS):
        return self._get_collector(message.CAPABILITY_TRADE, vendor)

    def get_available_request_collector(self, vendor=message.CYBOS):
        return self._get_available_collector(message.CAPABILITY_REQUEST_RESPONSE, vendor)

    def get_available_subscribe_collector(self, vendor=message.CYBOS):
        collector = None
        for c in self.get_vendor_collector(vendor):
            max_count = 380 if c.capability & message.CAPABILITY_TRADE else 400
            if c.capability & message.CAPABILITY_COLLECT_SUBSCRIBE and c.subscribe_count() < max_count:
                if collector is None:
                    collector = c
                else:
                    if collector.subscribe_count() > c.subscribe_count():
                        collector = c
        return collector

    def find_request_by_id(self, msg_id):
        for c in self.collectors:
            if c.request_id() == msg_id:
                return c
        return None

    def connect_to_subscribe(self, code, sock, header, body):
        if code in self.code_subscribe_info:
            found = False
            for s in self.code_subscribe_info[code][1]:
                if s == sock:
                    found = True
                    break
            if not found:
                self.code_subscribe_info[code][1].append(sock)
        else:
            collector = self.get_available_subscribe_collector()
            if collector is None:
                logger.error('NO AVAILABLE Subscribe collector')
            else:
                collector.append_subscribe_code(code)
                self.code_subscribe_info[code] = (collector, [sock])
                logger.info('ADD NEW SUBSCRIBE %s', code)
                stream_write(collector.sock, header, body, self)

    def disconnect_to_subscribe(self, code, sock, heaer, body):
        if code in self.code_subscribe_info:
            self.code_subscribe_info[code][1].remove(sock) 
            if len(self.code_subscribe_info[code][1]) == 0:
                collector = self.code_subscribe_info[code][0]
                collector.remove_subscribe_code(code)
                stream_write(collector.sock, header, body, self)
        else:
            logger.warning('No subscribe but try to disconnect %s', code)

    def connect_to_trade_subscribe(self, sock, vendor):
        collector = self.get_trade_collector(vendor)
        if collector is None:
            logger.error('NO TRADE collector %s', vendor)
            return
        if sock not in self.trade_subscribe_sockets[vendor]:
            self.trade_subscribe_sockets[vendor].append(sock)
        else:
            logger.warning('Sock is already connected to trade subscriber %s', vendor)
             

    def disconnect_to_trade_subscribe(self, sock, vendor):
        collector = self.get_trade_collector(vendor)
        if collector is None:
            logger.error('NO TRADE collector %s', vendor)
            return
        if sock in self.trade_subscribe_sockets[vendor]:
            self.trade_subscribe_sockets[vendor].remove(sock)

        if len(self.trade_subscribe_sockets[vendor]):
            pass # TODO: send STOP message

    def broadcast_trade_data(self, header, body, vendor):
        for s in self.trade_subscribe_sockets[vendor]:
            stream_write(s, header, body, self)

    def reset(self):
        pass

    def handle_block_request(self, sock, header, body):
        collector = self.get_available_request_collector()
        if collector is None:
            logger.critical('Cannot find collector(request) %s', header)
            return
        collector.set_request(sock, header['_id'], True)
        stream_write(collector.sock, header, body, self)

    def handle_block_response(self, sock, header, body):
        collector = self.find_request_by_id(header['_id'])
        if collector is None:
            logger.critical('Cannot find collector(response) %s', header)    
            return
        collector.set_pending(False)
        stream_write(collector,request_socket(), header, body, self)

    def handle_trade_block_request(self, sock, header, body):
        collector = self.get_available_trade_collector()
        if collecor is None:
            logger.critical('Cannot find collector(trade) %s', header)
            return
        collector.set_request(sock, header['_id'], True)
        stream_write(collector.sock, header, body, self)

    def handle_trade_block_response(self, sock, header, body):
        collector = self.find_request_by_id(header['_id'])
        if collector is None:
            logger.critical('Cannot find collector(trade response) %s', header)
            return
        collector.set_pending(False)
        stream_write(collector.sock, header, body, self)
