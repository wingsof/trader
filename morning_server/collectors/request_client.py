from gevent import monkey; monkey.patch_all()

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.join(*(['..' + os.sep] * 2)))))

import socket
import gevent
import time
from PyQt5.QtCore import QCoreApplication

from morning_server import message, stream_readwriter
from morning_server.collectors.cybos_api import stock_chart, stock_subscribe, bidask_subscribe, connection, stock_code, abroad_chart
from morning_server.collectors.cybos_api import trade_util, long_manifest_6033, order, modify_order, cancel_order, order_in_queue, balance, trade_subject
from configs import client_info
from utils import rlogger


def handle_request(sock, header, body):
    rlogger.info('REQUEST ' + str(header))
    header['type'] = message.RESPONSE
    if header['method'] == message.DAY_DATA:
        _, data = stock_chart.get_day_period_data(header['code'], header['from'], header['until'])
        stream_readwriter.write(sock, header, data)
    elif header['method'] == message.MINUTE_DATA:
        _, data = stock_chart.get_min_period_data(header['code'], header['from'], header['until'])
        stream_readwriter.write(sock, header, data)
    elif header['method'] == message.ABROAD_DATA:
        _, data = abroad_chart.get_period_data(header['code'], header['period_type'], header['count'])
        stream_readwriter.write(sock, header, data)
    elif header['method'] == message.CODE_DATA:
        if header['market_type'] == message.KOSPI:
            stream_readwriter.write(sock, header, stock_code.get_kospi_company_code_list())
        elif header['market_type'] == message.KOSDAQ:
            stream_readwriter.write(sock, header, stock_code.get_kosdaq_company_code_list())


def callback_stock_subscribe(sock, code, datas):
    header = stream_readwriter.create_header(message.SUBSCRIBE_RESPONSE, message.MARKET_STOCK, message.STOCK_DATA)
    header['code'] = code
    stream_readwriter.write(sock, header, datas)


def callback_bidask_subscribe(sock, code, datas):
    header = stream_readwriter.create_header(message.SUBSCRIBE_RESPONSE, message.MARKET_STOCK, message.BIDASK_DATA)
    header['code'] = code + message.BIDASK_SUFFIX
    stream_readwriter.write(sock, header, datas)


def callback_subject_subscribe(sock, code, datas):
    header = stream_readwriter.create_header(message.SUBSCRIBE_RESPONSE, message.MARKET_STOCK, message.SUBJECT_DATA)
    header['code'] = code + message.SUBJECT_SUFFIX
    stream_readwriter.write(sock, header, datas)


def callback_trade_subscribe(sock, result):
    header = stream_readwriter.create_header(message.TRADE_SUBSCRIBE_RESPONSE, message.MARKET_STOCK, message.TRADE_DATA)
    stream_readwriter.write(sock, header, result)


def get_order_subscriber(sock):
    global order_subscriber
    if order_subscriber is None:
        order_subscriber = order.Order(sock, account.get_account_number(), account.get_account_type(), callback_trade_subscribe)
    return order_subscriber


def handle_trade_request(sock, header, body):
    rlogger.info('TRADE REQUEST ' + str(header))
    header['type'] = message.RESPONSE_TRADE
    if header['method'] == message.GET_LONG_LIST:
        lm = long_manifest_6033.LongManifest(account.get_account_number(), account.get_account_type())
        stream_readwriter.write(sock, header, lm.get_long_list())
    elif header['method'] == message.BALANCE:
        account_balance = balance.get_balance(account.get_account_number(), account.get_account_type())
        stream_readwriter.write(sock, header, {'balance': account_balance})
    elif header['method'] == message.ORDER_STOCK:
        code = header['code']
        quantity = header['quantity']
        price = header['price']
        is_buy = header['trade_type'] == message.ORDER_BUY
        status, msg = get_order_subscriber(sock).process(code, quantity, account.get_account_number(), account.get_account_type(), price, is_buy)
        result = {'status': status, 'msg': msg}
        stream_readwriter.write(sock, header, result)
    elif header['method'] == message.MODIFY_ORDER:
        modify_order_obj = modify_order.ModifyOrder(account.get_account_number(), account.get_account_type())
        order_num = header['order_number']
        code = header['code']
        price = header['price']
        new_order_num = modify_order_obj.modify_order(order_num, code, 0, price)
        result = {'order_number': new_order_num}
        stream_readwriter.write(sock, header, result)
    elif header['method'] == message.TRADE_DATA:
        #TODO: handle multiple clients
        get_order_subscriber(sock)
        result = {'result': True}
        stream_readwriter.write(sock, header, result)
        rlogger.info('START ORDER SUBSCRIBE')
    elif header['method'] == message.CANCEL_ORDER:
        cancel_order_obj = cancel_order.CancelOrder(account.get_account_number(), account.get_account_type())
        order_num = header['order_number']
        code = header['code']
        amount = header['amount']
        result = cancel_order_obj.cancel_order(order_num, code, amount)
        result = {'result': result}
        stream_readwriter.write(sock, header, result)
    elif header['method'] == message.ORDER_IN_QUEUE:
        order_queue = order_in_queue.OrderInQueue(account.get_account_number(), account.get_account_type())
        result = order_queue.request()
        stream_readwriter.write(sock, header, result)

def handle_subscribe(sock, header, body):
    code = header['code']
    if header['method'] == message.STOCK_DATA:
        if code in subscribe_stock:
            rlogger.info('Already subscribe stock ' + code)
        else:
            subscribe_stock[code] = stock_subscribe.StockSubscribe(sock, code)
            subscribe_stock[code].start_subscribe(callback_stock_subscribe)
            rlogger.info('START Subscribe stock' + code)
    elif header['method'] == message.STOP_STOCK_DATA:
        if code in subscribe_stock:
            subscribe_stock[code].stop_subscribe()
            subscribe_stock.pop(code, None)
    elif header['method'] == message.BIDASK_DATA:
        codes = code.split('_')
        if len(codes) != 2:
            rlogger.info('Invalid subject code ' + code)
        else:
            code = codes[0]
            if code in subscribe_bidask:
                rlogger.info('Already subscribe bidask ' + code)
            else:
                subscribe_bidask[code] = bidask_subscribe.BidAskSubscribe(sock, code)
                subscribe_bidask[code].start_subscribe(callback_bidask_subscribe)
                rlogger.info('START Subscribe bidask ' + code)
    elif header['method'] == message.STOP_BIDASK_DATA:
        if code in subscribe_bidask:
            subscribe_bidask[code].stop_subscribe()
            subscribe_bidask.pop(code, None)
    elif header['method'] == message.SUBJECT_DATA:
        codes = code.split('_')
        if len(codes) != 2:
            rlogger.info('Invalid subject code ' + code)
        else:
            code = codes[0]
            if code in subscribe_subject:
                rlogger.info('Already subscribe subject ' + code)
            else:
                    code = codes[0]
                    subscribe_subject[code] = trade_subject.TradeSubject(sock, code)
                    subscribe_subject[code].start_subscribe(callback_subject_subscribe)
                    rlogger.info('START Subscribe subject ' + code)
    elif header['method'] == message.STOP_SUBJECT_DATA:
        if code in subscribe_subject:
            subscribe_subject[code].stop_subscribe()
            subscribe_subject[code].pop(code, None)
        

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
    app = QCoreApplication([])
    conn = connection.Connection()
    while not conn.is_connected():
        rlogger.info('Retry connecting to CP Server')
        gevent.sleep(5)

    rlogger.info('Connected to CP Server')
    subscribe_stock = dict()
    subscribe_bidask = dict()
    subscribe_subject = dict()
    order_subscribe = []

    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = (message.SERVER_IP, message.CLIENT_SOCKET_PORT)
            sock.connect(server_address)
            rlogger.info('Connected to apiserver')
            break
        except socket.error:
            rlogger.info('Retrying connect to apiserver')
            gevent.sleep(1)

    header = stream_readwriter.create_header(message.COLLECTOR, message.MARKET_STOCK, message.COLLECTOR_DATA)

    if client_info.get_client_capability() & message.CAPABILITY_TRADE:
        body = {'capability': message.CAPABILITY_COLLECT_SUBSCRIBE | message.CAPABILITY_TRADE}
    else:
        body = {'capability': message.CAPABILITY_REQUEST_RESPONSE | message.CAPABILITY_COLLECT_SUBSCRIBE}
    stream_readwriter.write(sock, header, body)

    if body['capability'] & message.CAPABILITY_TRADE:
        account = trade_util.TradeUtil()
        order_subscriber = None
        rlogger.info('HAS TRADE CAPABILITY')
    
    gevent.joinall([gevent.spawn(dispatch_message, sock), gevent.spawn(mainloop, app)])
