from gevent import monkey; monkey.patch_all()

import uuid
import pickle
import gevent
from gevent.event import Event
import threading
import socket
import errno

from morning_server import message

READ_PACKET_SIZE=4096
HEADER_SIZE=8


class MessageReader(gevent.Greenlet):
    def __init__(self, sock):
        super().__init__()
        self.sock = sock
        self.clients = dict()
        self.subscribers = dict()
        self.trade_subscriber = None
        self._stop_event = Event()

    def block_write(self, header, body):
        msg_id = header['_id']
        self.clients[msg_id] = [Event(), None]
        write(self.sock, header, body)
        self.clients[msg_id][0].wait()
        obj = self.clients[msg_id][1]
        self.clients.pop(msg_id, None)
        return obj

    def subscribe_write(self, header, body, code, handler):
        if code in self.subscribers:
            print('Already subscribe code', code)
        else:
            self.subscribers[code] = handler
            header['code'] = code
            write(self.sock, header, body)

    def stop_subscribe_write(self, header, body, code):
        if code in self.subscribers:
            self.subscribers.pop(code, None)
            header['code'] = code
            write(self.sock, header, body)
        else:
            print('Not subscribing code', code)

    def subscribe_trade_write(self, header, body, handler):
        # multiple listener?
        self.trade_subscriber = handler
        write(self.sock, header, body)

    def _run(self):
        full_msg = b''
        new_msg = True
        header_len = 0

        while True:
            try:
                rcv = read(self.sock, full_msg, new_msg, header_len)
                full_msg = rcv['packet_info'][0]
                new_msg = rcv['packet_info'][1]
                header_len = rcv['packet_info'][2]
            except:
                raise

            #print('recv threading', threading.get_ident())
            #print('HEADER', rcv['header'])
            msg_id = rcv['header']['_id'] 
            header_type = rcv['header']['type']
            if msg_id in self.clients:
                self.clients[msg_id][1] = rcv['body'].copy()
                #print('BODY', rcv['body'])
                self.clients[msg_id][0].set()
            elif header_type == message.SUBSCRIBE_RESPONSE:
                code = rcv['header']['code']
                #print('BODY', rcv['body'])
                self.subscribers[code](code, rcv['body'])
            elif header_type == message.TRADE_SUBSCRIBE_RESPONSE:
                if self.trade_subscriber is not None:
                    self.trade_subscriber(rcv['body'])

def create_header(header_type, market_type, method_name, vendor='cybos'):
    return {'type': header_type, 
            'market': market_type,
            'method': method_name,
            'vendor': vendor,
            '_id': str(uuid.uuid4())}


def write(sock, header, body):
    msg = {'header': header, 'body': body}
    msg = pickle.dumps(msg)
    msg = bytes(f"{len(msg):<{HEADER_SIZE}}", 'utf-8') + msg
    total_len = len(msg)
    try:
        while True:
            sent = sock.send(msg)
            total_len -= sent
            if total_len == 0:
                break
            else:
                msg = msg[sent:]

    except Exception as e:
        raise Exception(e.args[0], sock)


def read(sock, full_msg, new_msg, header_len):
    while True:
        if new_msg and len(full_msg) >= HEADER_SIZE:
            pass
        else:
            try:
                msg = sock.recv(READ_PACKET_SIZE)
            except socket.error as e:
                err = e.args[0]
                if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                    print('No data available')
                    continue
                else:
                    raise Exception('Socket Error ' + e.args[0], sock)

            if len(msg) == 0:
                raise Exception('Length 0 Socket error', sock)

            #print('receive', len(msg))
            full_msg += msg

        if new_msg:
            if len(full_msg) < HEADER_SIZE:
                continue
            header_len = int(full_msg[:HEADER_SIZE])
            new_msg = False
            full_msg = full_msg[HEADER_SIZE:]

        if not new_msg:
            #print('new_msg')
            if len(full_msg) < header_len:
                continue

            data = full_msg[:header_len]
            full_msg = full_msg[header_len:]
            new_msg = True
            data = pickle.loads(data)
            return {**data, 'packet_info': (full_msg, new_msg, header_len)}

    return None


def dispatch_message(sock, 
                    collector_handler = None, 
                    request_handler=None, 
                    response_handler = None, 
                    subscribe_handler=None, 
                    subscribe_response_handler=None,
                    request_trade_handler=None,
                    response_trade_handler=None,
                    subscribe_trade_response_handler=None):
    full_msg = b''
    new_msg = True
    header_len = 0

    while True:
        try:
            packet = read(sock, full_msg, new_msg, header_len)
            full_msg = packet['packet_info'][0]
            new_msg = packet['packet_info'][1]
            header_len = packet['packet_info'][2]
        except:
            raise

        header_type = packet['header']['type']
        if header_type == message.REQUEST and request_handler is not None:
            request_handler(sock, packet['header'], packet['body'])
        elif header_type == message.SUBSCRIBE and subscribe_handler is not None:
            subscribe_handler(sock, packet['header'], packet['body'])
        elif header_type == message.COLLECTOR and collector_handler is not None:
            collector_handler(sock, packet['header'], packet['body'])
        elif header_type == message.RESPONSE and response_handler is not None:
            response_handler(sock, packet['header'], packet['body'])
        elif header_type == message.SUBSCRIBE_RESPONSE and subscribe_response_handler is not None:
            subscribe_response_handler(sock, packet['header'], packet['body'])
        elif header_type == message.REQUEST_TRADE and request_trade_handler is not None:
            request_trade_handler(sock, packet['header'], packet['body'])
        elif header_type == message.RESPONSE_TRADE and response_trade_handler is not None:
            response_trade_handler(sock, packet['header'], packet['body'])
        elif header_type == message.TRADE_SUBSCRIBE_RESPONSE and subscribe_trade_response_handler is not None:
            subscribe_trade_response_handler(sock, packet['header'], packet['body'])
        else:
            print('Unknown header type', packet['header'])
            
