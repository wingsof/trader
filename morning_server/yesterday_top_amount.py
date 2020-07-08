from gevent import monkey; monkey.patch_all()

from pymongo import MongoClient
from configs import db


def get_yesterday_top_amount(date):
    collection = MongoClient(db.HOME_MONGO_ADDRESS)['trade_alarm']
    ydata = list(collection['yamount'].find({'date': date}))
    if len(ydata) == 1:
        return ydata[0]['codes']
    return []
