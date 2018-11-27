import sys
from PyQt5.QtCore import QCoreApplication, QTimer
sys.path.append('/usr/lib/virtualbox')
from datetime import datetime
import virtualbox
from utils import speculation
from dbapi import stock_code

class Machine:
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
        self.timer = QTimer()
        self.timer.timeout.connect(self.time_check)
        print('Get VirtualBox')
        self.vbox = virtualbox.VirtualBox()
        self.vbox_list = [vm.name for vm in self.vbox.machines]
        self.subscriber = None
        self.trader = None
        self.last_speculation_date = datetime(2018, 1, 1)
        print(self.vbox_list)

    def time_check(self):
        now = datetime.now()
        print(now, 'TIME CHECK')
        subscriber_cycle = (datetime(now.year, now.month, now.day, 7, 0, 0),
                            datetime(now.year, now.month, now.day, 18, 30, 0))
        trader_cycle = (datetime(now.year, now.month, now.day, 7, 30, 0),
                            datetime(now.year, now.month, now.day, 17, 0, 0))

        if self.subscriber is None and now >= subscriber_cycle[0] and now <= subscriber_cycle[1]:
            self.subscriber = Machine(self.vbox, 'win64')
            print(now, 'Running Subscriber')
        elif self.subscriber is not None and (now < subscriber_cycle[0] or now > subscriber_cycle[1]):
            self.subscriber.stop()
            self.subscriber = None
            print(now, 'Stop Subscriber')

        if self.trader is None and now >= trader_cycle[0] and now <= trader_cycle[1]:
            self.trader = Machine(self.vbox, 'win64-trader')
            print(now, 'Running Trader')
        elif self.trader is not None and (now < trader_cycle[0] or now > trader_cycle[1]):
            self.trader.stop()
            self.trader = None
            print(now, 'Stop Trader')

        if now.hour >= 4 and (self.last_speculation_date.year != now.year or self.last_speculation_date.month != now.month or self.last_speculation_date.day != now.day):
            if self.subscriber is None and self.trader is None:
                self.last_speculation_date = now
                print('Start Speculation Processing')
                speculation.Speculation().get_speculation(now, stock_code.get_kospi200_list())
                print('Done Speculation Processing')
            else:
                print('Already machine running, skip pre-speculating')

    def start(self):
        self.timer.start(60000)

if __name__ == '__main__':
    app = QCoreApplication(sys.argv)
    vbox = VBoxControl()
    vbox.start()
    app.exec()