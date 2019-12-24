import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import socket

import message
import stream_readwriter
from cybos_api import stock_chart


def request_handler(sock, header, body):
    if header['method'] == message.DAY_DATA:
        _, data = stock_chart.get_day_period_data(body['code'], body['from'], body['until'])
        header['type'] = message.RESPONSE
        stream_readwriter.write(sock, header, data)


def subscribe_handler(sock, header, body):
    if header['method'] == message.SUBSCRIBE:
        pass


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (message.SERVER_IP, message.CLIENT_SOCKET_PORT)
    
    # TODO: try, except and retry?
    sock.connect(server_address)
    header = stream_readwriter.create_header(message.COLLECTOR, message.MARKET_STOCK, message.COLLECTOR_DATA)
    body = {'capability': message.CAPABILITY_REQUEST_RESPONSE | message.CAPABILITY_COLLECT_SUBSCRIBE}
    stream_readwriter.dispatch_message(sock, None, request_handler, subscribe_handler)
    






    