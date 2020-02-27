from gevent import monkey; monkey.patch_all()
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 1))))


from clients.common import morning_client
from datetime import datetime, date, timedelta, time
from morning.back_data import holidays
from morning_server import stock_api, message
import gevent
from gevent.queue import Queue
from configs import db
from pymongo import MongoClient
from morning.pipeline.converter import dt
import numpy as np
from scipy.signal import find_peaks, peak_prominences
import pandas as pd




kosdaq_market_code = morning_client.get_market_code()
kospi_market_code = morning_client.get_market_code(message.KOSPI)

kosdaq_market_code.extend(kospi_market_code)

print(len(kosdaq_market_code))
