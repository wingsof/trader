from gevent import monkey; monkey.patch_all()

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.join(*(['..' + os.sep] * 2)))))

import socket
import gevent
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QAxContainer import QAxWidget

from morning_server import message, stream_readwriter
from configs import client_info
from utils import rlogger

from morning_server.collectors.kiwoom_api import investor_accumulate


def receive_trdata(screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
    if prev_next == '2': #TODO
        pass

    if rqname in request_dict:
        data = request_dict[rqname]
        
        if data[2] == message.INVESTOR_ACCUMULATE_DATA:
            result = investor_accumulate.get_data(ax_obj, rqname, trcode)
            stream_readwriter.write(data[0], data[1], result)

        request_dict.pop(rqname, None)


def handle_request(sock, header, body):
    rlogger.info('REQUEST ' + str(header))
    header['type'] = message.RESPONSE
    if header['method'] == message.INVESTOR_ACCUMULATE_DATA:
        request_dict[header['_id']] = (sock, header, message.INVESTOR_ACCUMULATE_DATA)
        investor_accumulate.request(ax_obj, header['_id'], header['code'], header['from'], header['until'])


def mainloop(app):
    while True:
        app.processEvents()
        while app.hasPendingEvents():
            app.processEvents()
            gevent.sleep()
        gevent.sleep()


def dispatch_message(sock):
    stream_readwriter.dispatch_message(sock, request_handler=handle_request)


def event_connect(err_code):
    if err_code == 0:
        rlogger.info('Connected to KIWOOM Server')
        ax_obj.OnReceiveTrData.connect(receive_trdata)
        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_address = (client_info.get_server_ip(), message.CLIENT_SOCKET_PORT)
                sock.connect(server_address)
                rlogger.info('Connected to apiserver')
                break
            except socket.error:
                rlogger.info('Retrying connect to apiserver')
                gevent.sleep(1)
        header = stream_readwriter.create_header(message.COLLECTOR, message.MARKET_STOCK, message.COLLECTOR_DATA, message.KIWOOM)
        body = {'capability': message.CAPABILITY_REQUEST_RESPONSE}
        stream_readwriter.write(sock, header, body)


if __name__ == '__main__':
    app = QApplication([])
    request_dict = dict()

    ax_obj = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
    ax_obj.OnEventConnect.connect(event_connect)

    ret = ax_obj.dynamicCall('CommConnect()')
    
    gevent.joinall([gevent.spawn(dispatch_message, sock), gevent.spawn(mainloop, app)])
