from gevent import monkey
monkey.patch_all()

import gevent
from datetime import datetime, timedelta


def tick_test():
    data = [{'date': datetime(2020,3,31,13,7,1,100)},
            {'date': datetime(2020,3,31,13,7,1,300)},
            {'date': datetime(2020,3,31,13,7,2,300)},
            {'date': datetime(2020,3,31,13,7,3,300)},
    ]
    now = datetime.now()
    datatime = None
    for d in data:
        if datatime is None:
            datatime = d['date'] - timedelta(seconds=1)

        #print(d['date'] - datatime, datetime.now() - now)
        while d['date'] - datatime > datetime.now() - now:
            gevent.sleep(0.02)

        print(d['date'])
        now = datetime.now()
        datatime = d['date']



tick_test()
