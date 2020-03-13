import gevent

from configs import client_info
if client_info.TEST_MODE:
    from clients.scalping_by_amount.mock import datetime
else:
    from datetime import datetime

from datetime import timedelta

def sleep(sec):
    now = datetime.now()
    while datetime.now() - now < timedelta(seconds=sec):
        gevent.sleep(0.005)
