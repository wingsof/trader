from gevent import monkey; monkey.patch_all()

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import socket
import gevent

import message
import stream_readwriter
import time
from cybos_api import stock_chart, stock_subscribe, bidask_subscribe, connection
from PyQt5.QtCore import QCoreApplication


def handle_request(sock, header, body):
    print('request_handler')
    if header['method'] == message.DAY_DATA:
        _, data = stock_chart.get_day_period_data(header['code'], header['from'], header['until'])
        header['type'] = message.RESPONSE
        stream_readwriter.write(sock, header, data)


def callback_stock_subscribe(sock, code, datas):
    header = stream_readwriter.create_header(message.SUBSCRIBE_RESPONSE, message.MARKET_STOCK, message.STOCK_DATA)
    header['code'] = code
    stream_readwriter.write(sock, header, datas)


def callback_bidask_subscribe(sock, code, datas):
    header = stream_readwriter.create_header(message.SUBSCRIBE_RESPONSE, message.MARKET_STOCK, message.BIDASK_DATA)
    header['code'] = code
    stream_readwriter.write(sock, header, datas)


def handle_trade_request(sock, header, body):
    pass


def handle_subscribe(sock, header, body):
    code = header['code']
    if header['method'] == message.STOCK_DATA:
        if code in subscribe_stock:
            print('Already subscribe stock', code)
        else:
            subscribe_stock[code] = stock_subscribe.StockSubscribe(sock, code)
            subscribe_stock[code].start_subscribe(callback_stock_subscribe)
            print('START Subscribe stock', code)
    elif header['method'] == message.STOP_STOCK_DATA:
        if code in subscribe_stock:
            subscribe_stock[code].stop_subscribe()
            subscribe_stock.pop(code, None)
    elif header['method'] == message.BIDASK_DATA:
        if code in subscribe_bidask:
            print('Already subscribe bidask', code)
        else:
            subscribe_bidask[code] = bidask_subscribe.BidAskSubscribe(sock, code)
            subscribe_bidask[code].start_subscribe(callback_bidask_subscribe)
            print('START Subscribe bidask', code)
    elif header['method'] == message.STOP_BIDASK_DATA:
        if code in subscribe_bidask:
            subscribe_bidask[code].stop_subscribe()
            subscribe_bidask.pop(code, None)
        

def mainloop(app):
    while True:
        app.processEvents()
        while app.hasPendingEvents():
            app.processEvents()
            gevent.sleep()
        gevent.sleep()


def dispatch_message(sock):
    stream_readwriter.dispatch_message(sock, request_handler=handle_request, 
                                        subscribe_handler=handle_subscribe, 
                                        request_trade_handler=handle_trade_request)


if __name__ == '__main__':
    # TODO: CpUtil 
    app = QCoreApplication([])
    conn = connection.Connection()
    while not conn.is_connected():
        print('Retry connecting to CP Server')
        gevent.sleep(5)

    subscribe_stock = dict()
    subscribe_bidask = dict()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (message.SERVER_IP, message.CLIENT_SOCKET_PORT)
    
    # TODO: try, except and retry?
    sock.connect(server_address)
    header = stream_readwriter.create_header(message.COLLECTOR, message.MARKET_STOCK, message.COLLECTOR_DATA)
    body = {'capability': message.CAPABILITY_REQUEST_RESPONSE | message.CAPABILITY_COLLECT_SUBSCRIBE}
    stream_readwriter.write(sock, header, body)

    if body['capability'] | message.CAPABILITY_TRADE:
        # TODO: start subscribe, cpconclusion
        pass
    
    gevent.joinall([gevent.spawn(dispatch_message, sock), gevent.spawn(mainloop, app)])
