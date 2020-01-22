#!/usr/bin/env python
from gevent import monkey
monkey.patch_all()
monkey.patch_sys(stdin=True, stdout=False, stderr=False)


import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from gevent.fileobject import FileObject
import gevent
from gevent.queue import Queue
import sys
import signal

import socket
from morning_server import message
from morning_server import stock_api
from morning_server import stream_readwriter
from morning_server import stock_api


sys.stdin = FileObject(sys.stdin)
q = Queue()


def producer():
    while True:
        line = sys.stdin.readline()
        q.put(line)


def display_trade_result(result):
    print(result)


def consumer():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (message.SERVER_IP, message.CLIENT_SOCKET_PORT)
    sock.connect(server_address)

    message_reader = stream_readwriter.MessageReader(sock)
    message_reader.start()

    stock_api.subscribe_trade(message_reader, display_trade_result)
    while True:
        val = q.get(True)
        command = val.decode('ascii').rstrip()
        print(command)

        if command == 'long':
            print(stock_api.request_long_list(message_reader))
        elif command.startswith('buy') or command.startswith('sell'):
            buy_detail = command.split(',')
            print(buy_detail)
            if len(buy_detail) != 4:
                print('buy|sell,code,price,quantity')
            else:
                is_buy = True
                if buy_detail[0] == 'buy':
                    pass
                elif buy_detail[0] == 'sell':
                    is_buy = False
                else:
                    print('wrong buy/sell command')
                    continue
                code = buy_detail[1]
                price = int(buy_detail[2])
                quantity = int(buy_detail[3])
                result = stock_api.order_stock(message_reader, code, price, quantity, is_buy)
                print(result)
        elif command_startswith('modify'):
            modify_detail = command.split(',')
            if len(modify_detail) != 4:
                print('modify,order_num,code,price')
            else:
                order_num = int(modify_detail[1])
                code = modify_detail[2]
                price = int(modify_detail[3])
                result = stock_api.modify_order(message_reader, order_num, code, price)
                print(result)
        elif command_startswith('cancel'):
            cancel_detail = command.split(',')
            if len(cancel_detail) != 4:
                print('cancel,order_num,code,amount')
            else:
                order_num = int(cancel_detail[1])
                code = cancel_detail[2]
                amount = int(cancel_detail[3])
                result = stock_api.cancel_order(message_reader, order_num, code, amount)
                print(result)


def main():
    gevent.signal(signal.SIGQUIT, gevent.kill)

    greenlets = [
        gevent.spawn(consumer),
        gevent.spawn(producer),
    ]

    try:
        gevent.joinall(greenlets)
    except KeyboardInterrupt:
        print("Exiting...")


if __name__ == '__main__':
    main()
