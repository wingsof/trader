from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import date, timedelta, datetime
import gevent
import socket
import sys
from datetime import date
import time
import threading
import pandas as pd
import numpy as np

from morning_server import message
from morning_server import stock_api
from morning_server import stream_readwriter
from morning.back_data import holidays
from morning.pipeline.converter import dt
from utils import time_converter
from morning_server import trendfinder


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = (message.SERVER_IP, message.CLIENT_SOCKET_PORT)
sock.connect(server_address)

message_reader = stream_readwriter.MessageReader(sock)
message_reader.start()

market_code = stock_api.request_stock_code(message_reader, message.KOSDAQ)


from_date = date(2019, 10, 1)
until_date = date(2019, 10, 30)

while from_date <= until_date:
    if holidays.is_holidays(from_date):
        from_date += timedelta(days=1)
        continue

    yesterday = holidays.get_yesterday(from_date)
    yesterday_data = []
    
    for code in market_code:
        data = stock_api.request_stock_day_data(message_reader, code, from_date, from_date)
        data['code'] = code
        yesterday_data.append(dt.cybos_stock_day_tick_convert(data))

    yesterday_data = sorted(yesterday_data, key=lambda x: x['amount'], reverse=True)
    yesterday_data = yesterday_data[:150]

    candidate_codes = []
    for data in yesterday_data:
        if data['cum_buy_volume'] > data['cum_sell_volume']:
            candidate_codes.append(data)
    


