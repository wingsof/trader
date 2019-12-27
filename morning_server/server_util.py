from morning_server import stream_readwriter
from morning_server import message


def datetime_to_intdate(dt):
    return dt.year * 10000 + dt.month * 100 + dt.day


def stream_write(sock, header, body, manager = None):
    try:
        stream_readwriter.write(sock, header, body)
    except Exception as e:
        print('Stream write error', e)
        if manager is not None:
            manager.handle_disconnect(e.args[1])


class _Collector:
    def __init__(self, sock, capability):
        self.sock = sock
        self.capability = capability
        self.subscribe_code = []
        self.request = {
            'pending': False,
            'id': None,
            'socket': None,
            'periods': [],
            'data': [],
            'count': 0}

    def request_id(self):
        return self.request['id']

    def request_pending(self):
        return self.request['pending']

    def request_socket(self):
        return self.request(['socket'])

    def subscribe_count(self):
        return len(self.subscribe_code)

    def set_pending(self, is_pending):
        self.request['pending'] = is_pending

    def append_subscribe_code(self, code):
        self.subscribe_code.append(code)

    def set_request(self, sock, msg_id, is_pending):
        self.request['socket'] = sock
        self.request['id'] = msg_id
        self.request['pending'] = is_pending


class CollectorList:
    def __init__(self):
        self.collectors = []

    def add_collector(self, sock, body):
        self.collectors.append(_Collector(sock, body['capability']))

    def handle_disconnect(self, sock):
        print('HANDLE DISCONNECT: CollectorList')
        collector = None
        for c in self.collectors:
            if c.sock == sock:
                print('Collector Removed')
                collector = c
                break

        if collector is not None:
            # TODO: Notify collector disconnected events to clients
            self.collectors.remove(collector)

    def find_by_id(self, msg_id):
        for c in self.collectors:
            if c.request_id() == msg_id:
                return c
        return None

    def find_request_collector(self):
        for c in self.collectors:
            if c.capability | message.CAPABILITY_REQUEST_RESPONSE and not c.request_pending():
                return c
        return None

    def find_subscribe_collector(self):
        collector = None
        for c in self.collectors:
            if c.capability | message.CAPABILITY_COLLECT_SUBSCRIBE and c.subscribe_count() < 400:
                if collector is None:
                    collector = c
                else:
                    if len(collector['subscribe_code']) > len(c['subscribe_code']):
                        collector = c
        return collector


class SubscribeClient:
    def __init__(self):
        # Key: code, Values: (collector_socket, [subscribe_client_socket, ])
        self.clients = dict()

    def code_in_clients(self, code):
        return code in self.clients

    def send_to_clients(self, code, header, body):
        if self.code_in_clients(code):
            for s in self.clients[code][1]:
                stream_write(s, self, header, body, self)

    def handle_disconnect(self, sock):
        print('HANDLE DISCONNECT: SubscribeClient')
        for v in self.clients.values():
            for s in v[1]:
                if s == sock:
                    # Assume that sock is not duplicated in a code
                    print('Client Removed')
                    v[1].remove(sock)
                    break

    def add_to_clients(self, code, sock, collectors):
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
                pass # TODO return FULL
            else:
                collector.append_subscribe_code(code)
                self.clients[code] = (collector.sock, [sock])
                stream_write(collector.sock, header, body, collectors)


class _Partial:
    def __init__(self, header, db_data, count):
        self.header = header
        self.data_type = header['method']
        self.count = count
        self.data = []
        self.db_data = db_data

    def add_body(self, body, header):
        self.data.append(body)

        if len(body) == 0:
            print('RECORD DATA to DB as EMPTY', header['method'], header['code'], header['from'], header['until'])
        else:
            print('RECORD DATA to DB', header['method'], header['code'], header['from'], header['until'])

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
        self.client[header['_id']] = Partial(header, data, count)

    def get_item(self, msg_id):
        if msg_id in self.client:
            return self.client[msg_id]

        return None

    def pop_item(self, msg_id):
        if msg_id in self.client:
            self.client.pop(msg_id, None)
