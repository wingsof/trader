from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gevent.server import StreamServer
from datetime import datetime
import threading
import time
import gevent
import virtualbox
from multiprocessing import Process
from gevent.queue import Queue

from morning_server import message
from morning.config import db
from morning_server import stream_readwriter
from utils import logger_server, logger
import virtualbox
import time
import gevent


vbox_on = False
tasks = Queue()
current_collector = 0


class _Machine:
    def __init__(self, vbox, vm_name):
        self.vbox = vbox
        self.vm_name = vm_name
        self.session = virtualbox.Session()
        vm = self.vbox.find_machine(self.vm_name)
        vm.launch_vm_process(self.session, 'gui', '')

    def stop(self):
        self.session.console.power_down()


class VBoxControl:
    def __init__(self):
        self.vbox = virtualbox.VirtualBox()
        self.vbox_list = [vm.name for vm in self.vbox.machines]
        self.vbox_machines = []
        print('VBOX List', self.vbox_list)

    def start_machine(self):
        for m in self.vbox_list:
            print('START Machine', m)
            self.vbox_machines.append(_Machine(self.vbox, m))            

    def stop_machine(self):
        for m in self.vbox_machines:
            print('STOP Machine', m.vm_name)
            m.stop()
            
        self.vbox_machines.clear()


def handle_collector(sock, header, body):
    global current_collector
    current_collector += 1

    if current_collector == 3:
        current_collector = 0
        tasks.put_nowait('stop')
        gevent.sleep(30)
        tasks.put_nowait('start')

def handle_response(sock, header, body):
    pass


def handle_request_cybos(sock, header, body):
    pass


def handle_request_kiwoom(sock, header, body):
    pass


def handle_request(sock, header, body):
    pass


def handle_subscribe(sock, header, body):
    pass

def handle_subscribe_response(sock, header, body):
    pass


def handle_trade_response(sock, header, body):
    pass


def handle_trade_request(sock, header, body):
    pass

def handle_trade_subscribe_response(sock, header, body):
    pass


def handle(sock, address):
    logger.info('new connection, address ' + str(address))
    try:
        stream_readwriter.dispatch_message(sock, collector_handler=handle_collector, 
                                            request_handler=handle_request,
                                            response_handler=handle_response, 
                                            subscribe_handler=handle_subscribe,
                                            subscribe_response_handler=handle_subscribe_response, 
                                            request_trade_handler=handle_trade_request,
                                            response_trade_handler=handle_trade_response,
                                            subscribe_trade_response_handler=handle_trade_subscribe_response)
    except Exception as e:
        logger.warning('Dispatch exception ' + str(e))
       

def vbox_control():
    global vbox_on
    vbox_controller = VBoxControl()
    while True:
        command = tasks.get()
        if command == 'start' and not vbox_on:
            vbox_on = True
            vbox_controller.start_machine()
        elif command == 'stop' and vbox_on:
            vbox_controller.stop_machine()
            vbox_on = False


log_server = Process(target=logger_server.start_log_server)
log_server.start()

server = StreamServer((message.SERVER_IP, message.CLIENT_SOCKET_PORT), handle)
server.start()

gevent.Greenlet.spawn(vbox_control)
tasks.put_nowait('start')
log_server.join()
