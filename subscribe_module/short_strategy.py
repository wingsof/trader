import connection
import stock_code
import time
import queue
import sys
import win32com.client
from datetime import datetime
from pymongo import MongoClient
import bidask_realtime
import stock_current_realtime

from multiprocessing import Process, Queue
from PyQt5.QtCore import QCoreApplication, QTimer
import db_info


class ShortCollector:
    SUBSCRIBE_PERIOD = 1
    def __init__(self, q):
        self.heart_beat = QTimer()
        self.queue = q
        self.heart_beat.timeout.connect(self.time_check)
        self.heart_beat.start(10000 * ShortCollector.SUBSCRIBE_PERIOD)
        self.current_subscribe_codes = []
        self.last_loop_time = [0, 0]
        self.realtime_subscribers = []
        self.client = MongoClient(db_info.HOME_MONGO_ADDRESS)

    def network_check(self):
        conn = connection.Connection()
        if not conn.is_connected():
            print('ALERT: Network not connected', flush=True)
            # do something to alert me

    def _loop_print(self):
        t = datetime.now()
        if self.last_loop_time[0] != t.hour or self.last_loop_time[1] != t.minute:
            print('Main Loop', self.queue.qsize(), t, flush=True)
            self.last_loop_time[0] = t.hour
            self.last_loop_time[1] = t.minute
            self.network_check()    

    def time_check(self):
        global current_subscribe_count
        #print("Queue Size: ", self.queue.qsize())
        codes = []
        while self.queue.qsize():
            try:
                codes = self.queue.get_nowait()
            except:
                break

        self._loop_print()
        print('SUBSCRIBE COUNT', current_subscribe_count)
        if current_subscribe_count >= 400:
            print('SUBSCRIBE COUNT REACH TO MAXIMUM')
            return

        code_diff = set(codes).difference(self.current_subscribe_codes)
        for code in code_diff:
            print('START SUBSCRIBE', code)
            bidask = bidask_realtime.StockRealtime(code, self.client)
            stock_current = stock_current_realtime.StockRealtime(code, self.client)
            self.realtime_subscribers.append(bidask)
            self.realtime_subscribers.append(stock_current)
            bidask.subscribe()
            stock_current.subscribe()
            current_subscribe_count += 2

        self.current_subscribe_codes.extend(list(code_diff))


class Cp7043:
    MAX_CODE_COUNT = 20
    KOSPI = 0
    KOSDAQ = 1

    def __init__(self, market):
        self.objRq = win32com.client.Dispatch("CpSysDib.CpSvrNew7043")
        if market == Cp7043.KOSPI:
            self.objRq.SetInputValue(0, ord('1')) # 코스닥
        else:
            self.objRq.SetInputValue(0, ord('2')) # 코스닥
        # 1 값에 값을 넣는 경우, 상승한 종목만 걸러냄
        self.objRq.SetInputValue(1, ord('2'))  # 상승()
        self.objRq.SetInputValue(2, ord('1'))  # 당일
        self.objRq.SetInputValue(3, 61)  # 거래대금 상위순
        self.objRq.SetInputValue(4, ord('2'))  # 관리 종목 포함
        self.objRq.SetInputValue(5, ord('0'))  # 거래량 전체
        self.objRq.SetInputValue(6, ord('0'))  # '표시 항목 선택 - '0': 시가대비
        self.objRq.SetInputValue(7, 0)  #  등락율 시작
        self.objRq.SetInputValue(8, 15)  # 등락율 끝
 
    def rq7043(self, retcode):
        self.objRq.BlockRequest()
        rqStatus = self.objRq.GetDibStatus()

        if rqStatus != 0:
            print("Connection Status", rqStatus)
            return False
 
        cnt = self.objRq.GetHeaderValue(0)
        cntTotal  = self.objRq.GetHeaderValue(1)
        #print(cnt, cntTotal)
 
        for i in range(cnt):
            code = self.objRq.GetDataValue(0, i)  # 코드
            retcode.append(code)

            if len(retcode) >=  Cp7043.MAX_CODE_COUNT:       # 최대 10 종목만,
                break
            name = self.objRq.GetDataValue(1, i)  # 종목명
            diffflag = self.objRq.GetDataValue(3, i)
            diff = self.objRq.GetDataValue(4, i)
            vol = self.objRq.GetDataValue(6, i)  # 거래량
            print(code, name, diffflag, diff, vol)

 
    def request(self, retCode):
        self.rq7043(retCode)
 
        if len(retCode) < Cp7043.MAX_CODE_COUNT:
            while self.objRq.Continue:
                self.rq7043(retCode)

                if len(retCode) >= Cp7043.MAX_CODE_COUNT:
                    print('break')
                    break
        
 
        return True


def start_short_code_collector(q):
    last_minute = current_minute = datetime.now().minute
    client = MongoClient(db_info.HOME_MONGO_ADDRESS)
    db = client.stock
    db['KOSDAQ_BY_TRADED']
    db['KOSPI_BY_TRADED']

    prev_kospi_codes = []
    prev_kosdaq_codes = []
    while True:
        if last_minute != current_minute:
            codes = []
            cp =  Cp7043(Cp7043.KOSPI)
            kospi_codes = []
            cp.request(kospi_codes)

            kosdaq_codes = []
            cp =  Cp7043(Cp7043.KOSDAQ)
            cp.request(kosdaq_codes)

            codes.extend(kospi_codes)
            codes.extend(kosdaq_codes)

            q.put(codes)
            last_minute = datetime.now().minute

            if len(set(kospi_codes).difference(prev_kospi_codes)) > 0:
                print('CODE HAS DIFFERENCES')
                d = {}
                d['date'] = datetime.now()
                for i, c in enumerate(kospi_codes):
                    d[str(i)] = c
                db['KOSPI_BY_TRADED'].insert_one(d)
                prev_kospi_codes = kospi_codes

            if len(set(kosdaq_codes).difference(prev_kosdaq_codes)) > 0:
                print('CODE HAS DIFFERENCES')
                d = {}
                d['date'] = datetime.now()
                for i, c in enumerate(kosdaq_codes):
                    d[str(i)] = c
                db['KOSDAQ_BY_TRADED'].insert_one(d)
                prev_kosdaq_codes = kosdaq_codes
        else:
            time.sleep(1)
            current_minute = datetime.now().minute


if __name__ == '__main__':
    #time.sleep(60*3)
    current_subscribe_count = 0
    conn = connection.Connection()
    while not conn.is_connected():
        time.sleep(5)
    
    q = Queue()
    p = Process(target = start_short_code_collector, args=(q,))
    p.start()
    print("Short Strategy", flush=True)

    
    app = QCoreApplication(sys.argv)
    sc = ShortCollector(q)
    app.exec()
