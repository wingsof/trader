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
from datetime import datetime, date

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
    print('TRADE', result)


def display_subject_data(code, data):
    print('SUBJECT', code, data)

def display_alarm_data(code, data):
    print('ALARM', data)


def display_bidask_data(code, data):
    print('BIDASK', code, data)


def display_stock_data(code, data):
    print('STOCK', code, data)


def display_world_data(code, data):
    print('WORLD', code, data)


def consumer():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (message.SERVER_IP, message.CLIENT_SOCKET_PORT)
    sock.connect(server_address)

    message_reader = stream_readwriter.MessageReader(sock)
    message_reader.start()

    #stock_api.subscribe_trade(message_reader, display_trade_result)
    while True:
        val = q.get(True)
        command = val.decode('ascii').rstrip()
        #print(command)

        if command == 'long':
            print(stock_api.request_long_list(message_reader))
        elif command.startswith('trade_subscribe'):
            stock_api.subscribe_trade(message_reader, display_trade_result)
        elif command.startswith('trade_stop_subscribe'):
            stock_api.stop_subscribe_trade(message_reader)
        elif command.startswith('todaym'):
            todaym_detail = command.split(',')
            if len(todaym_detail) != 2:
                print('todaym,code')
            else:
                result = stock_api.request_stock_today_data(message_reader, todaym_detail[1])
                if len(result) > 1:
                    print('DATA LEN', len(result))
                    print('HEAD', result[0])
                    print(result[1])
                    print('TAIL', result[-1])
        elif command.startswith('todayt'):
            todaym_detail = command.split(',')
            if len(todaym_detail) != 2:
                print('todayt,code')
            else:
                result = stock_api.request_stock_today_tick_data(message_reader, todaym_detail[1])
                if len(result) > 1:
                    print('DATA LEN', len(result))
                    print('HEAD', result[0])
                    print(result[1])
                    print('TAIL', result[-1])
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
        elif command.startswith('modify'):
            modify_detail = command.split(',')
            if len(modify_detail) != 4:
                print('modify,order_num,code,price')
            else:
                order_num = int(modify_detail[1])
                code = modify_detail[2]
                price = int(modify_detail[3])
                result = stock_api.modify_order(message_reader, order_num, code, price)
                print(result)
        elif command.startswith('cancel'):
            cancel_detail = command.split(',')
            if len(cancel_detail) != 4:
                print('cancel,order_num,code,amount')
            else:
                order_num = int(cancel_detail[1])
                code = cancel_detail[2]
                amount = int(cancel_detail[3])
                result = stock_api.cancel_order(message_reader, order_num, code, amount)
                print(result)
        elif command.startswith('queue'):
            print(stock_api.request_order_in_queue(message_reader))
        elif command.startswith('balance'):
            print(stock_api.get_balance(message_reader)['balance'])
        elif command.startswith('subject'):
            subject_detail = command.split(',')
            if len(subject_detail) != 2:
                print('subject,code')
            else:
                code = subject_detail[1]
                stock_api.subscribe_stock_subject(message_reader, code, display_subject_data)
        elif command.startswith('stop_subject'):
            subject_detail = command.split(',')
            if len(subject_detail) != 2:
                print('stop_subject,code')
            else:
                code = subject_detail[1]
                stock_api.stop_subscribe_stock_subject(message_reader, code)
        elif command.startswith('stop_bidask'):
            bidask_detail = command.split(',')
            if len(bidask_detail) != 2:
                print('stop_bidask,code')
            else:
                code = bidask_detail[1]
                stock_api.stop_subscribe_stock_bidask(message_reader, code)
        elif command.startswith('bidask'):
            bidask_detail = command.split(',')
            if len(bidask_detail) != 2:
                print('bidask,code')
            else:
                code = bidask_detail[1]
                stock_api.subscribe_stock_bidask(message_reader, code, display_bidask_data)
        elif command.startswith('stock'):
            stock_detail = command.split(',')
            if len(stock_detail) != 2:
                print('stock,code')
            else:
                code = stock_detail[1]
                stock_api.subscribe_stock(message_reader, code, display_stock_data)
        elif command.startswith('stop_stock'):
            stock_detail = command.split(',')
            if len(stock_detail) != 2:
                print('stop_stock,code')
            else:
                code = stock_detail[1]
                stock_api.stop_subscribe_stock(message_reader, code)
        elif command.startswith('req'):
            req_detail = command.split(',')
            if len(req_detail) != 2:
                print('req,code')
            else:
                code = req_detail[1]
                print(stock_api.request_stock_day_data(message_reader, code, date(2020,1,31), date(2020,1,31)))
        elif command.startswith('abroad'):
            abroad_detail = command.split(',')
            if len(abroad_detail) != 2:
                print('abroad,code')
            else:
                code = abroad_detail[1]
                print(stock_api.request_abroad_data(message_reader, code, message.PERIOD_DAY, 30))
        elif command.startswith('uscode'):
            #print(stock_api.request_us_stock_code(message_reader, message.USTYPE_ALL))
            print(len(stock_api.request_us_stock_code(message_reader, message.USTYPE_ALL)))
        elif command.startswith('world'):
            world_detail = command.split(',')
            if len(world_detail) != 2:
                print('world,code')
            else:
                code = world_detail[1]
                stock_api.subscribe_world(message_reader, code, display_world_data)
        elif command.startswith('stop_world'):
            world_detail = command.split(',')
            if len(world_detail) != 2:
                print('stop_world,code')
            else:
                code = world_detail[1]
                stock_api.stop_subscribe_world(message_reader, code)

        elif command.startswith('investor'):
            inv_detail = command.split(',')
            if len(inv_detail) != 2:
                print('investor,code')
            else:
                code = inv_detail[1]
                print(stock_api.request_investor_data(message_reader, code, date(2020,1,31), date(2020,1,31)))
        elif command.startswith('kinvestorc'):
            invc_detail = command.split(',')
            if len(invc_detail) != 2:
                print('investorc,code')
            else:
                code = invc_detail[1]
                print(stock_api.request_investor_accumulate_data(message_reader, code, date(2020,2,7), date(2020,2,7)))
        elif command.startswith('alarm'):
            stock_api.subscribe_alarm(message_reader, display_alarm_data)
        elif command.startswith('stop_alarm'):
            stock_api.stop_subscribe_alarm(message_reader)


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
