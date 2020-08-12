from gevent import monkey; monkey.patch_all()
from pymongo import MongoClient
from datetime import datetime, timedelta
from clients.common import morning_client
from morning_server import message
from morning.pipeline.converter import dt
import config
import preload


_today_list = {}
REFRESH_SEC = 180
_today_period_list = {}
_last_push_time = None


def get_today_list(opt, catch_plus, acculmulated):
    global REFRESH_SEC
    REFRESH_SEC = opt

    if acculmulated:
        selected_dict = _today_list
    else:
        selected_dict = _today_period_list

    code_list = []
    by_amount = sorted(selected_dict.items(), key=lambda x: x[1][0], reverse=True)

    if not catch_plus:
        return [b[0] for b in by_amount[:100]]

    for v in by_amount:
        if v[1][1] > v[1][2]:
            code_list.append(v[0])

            if len(code_list) >= 100:
                break

    _today_period_list.clear()
    _last_push_time = None

    return code_list


def clear_all():
    global _last_push_time
    _last_push_time = None
    _today_period_list.clear()
    _today_list.clear()


def handle_today_bull(code, d):
    global _last_push_time

    if d['cum_amount'] == 0:
        amount = d['cum_volume'] * d['current_price']
    else:
        if preload.is_kospi(code):
            amount = d['cum_amount'] * 10000
        else:
            amount = d['cum_amount'] * 1000

    if not preload.is_skip_ydata() and not preload.loading:
        yesterday_amount = preload.get_yesterday_amount(code)
        yesterday_close = preload.get_yesterday_close(code)

        if yesterday_amount < 3000000000 or yesterday_close * 1.15 < d['current_price']:
            _today_list[code] = [0, d['current_price'], d['current_price'] - d['yesterday_diff']]
        else:
            _today_list[code] = [amount / yesterday_amount, d['current_price'], d['current_price'] - d['yesterday_diff']]
    else:
        _today_list[code] = [amount, d['current_price'], d['current_price'] - d['yesterday_diff']]

    _today_period_list[code] = [d['current_price'] * d['volume'], d['current_price'], d['current_price'] - d['yesterday_diff']]

    if _last_push_time is None:
        _last_push_time = d['date']
    else:
        if d['date'] - _last_push_time > timedelta(seconds=REFRESH_SEC):
            _last_push_time = d['date']
            return config.CAND_TODAY_BUL

    return config.CAND_NONE
