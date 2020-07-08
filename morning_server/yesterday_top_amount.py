from gevent import monkey; monkey.patch_all()

from pymongo import MongoClient
from configs import db


def get_yesterday_top_amount(date):
    db = MongoClient(db.HOME_MONGO_ADDRESS)['trade_alarm']
    ydata = list(db['yamount'].find({'date': date}))
    if len(ydata) == 1:
        return ydata['codes']
    return []
