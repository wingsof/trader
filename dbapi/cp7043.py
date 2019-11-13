import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pymongo import MongoClient
import config


class Cp7043:
    # KOSDAQ FIXED
    def __init__(self):
        self.db = MongoClient(config.MONGO_SERVER)['stock']
 
    def request(self, codes_in):
        cursor = self.db['KOSDAQ_BY_TRADED'].find({})
        data = list(cursor)
        if len(data) > 0:
            last_data = list(data[-1].values())[2:]
            codes_in.extend(last_data)

if __name__ == '__main__':
    codes = []
    Cp7043().request(codes)
    
    print(codes)