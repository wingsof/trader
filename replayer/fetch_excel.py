from pymongo import MongoClient
import config
from datetime import datetime
import pandas as pd

if __name__ == '__main__':
    db = MongoClient(config.MONGO_SERVER).stock
    cursor = db['A035420'].find({'date': {'$gt': datetime(2018, 11, 23),
                                '$lt': datetime(2018, 11, 24)}})
    df = pd.DataFrame(list(cursor))
    writer = pd.ExcelWriter('A035420_11_23.xlsx')
    df.to_excel(writer, 'Sheet1')
    writer.save()