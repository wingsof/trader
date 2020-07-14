from gevent import monkey; monkey.patch_all()
from pymongo import MongoClient
from datetime import datetime, timedelta


_today_list = {}
REFRESH_SEC = 60
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
    global _today_list
    global _today_period_list
    global _last_push_time
    _last_push_time = None
    _today_period_list.clear()
    _today_list.clear()



def handle_today_tick(code, d):
    global _today_list
    global _last_push_time

    if d['10'] == 0:
        amount = d['9'] * d['13']
    else:
        amount = d['10']

    if code not in _today_list:
        _today_list[code] = [amount, d['13'], d['13'] - d['2']]
    else:
        _today_list[code][0] = amount
        _today_list[code][1] = d['13']
        _today_list[code][2] = d['13'] - d['2']

    if code not in _today_period_list:
        _today_period_list[code] = [d['13'] * d['17'], d['13'], d['13'] - d['2']]
    else:
        _today_period_list[code][0] += d['13'] * d['17']
        _today_period_list[code][1] = d['13']
        _today_period_list[code][2] = d['13'] - d['2']

    if _last_push_time is None:
        _last_push_time = d['date']
    else:
        if d['date'] - _last_push_time > timedelta(seconds=REFRESH_SEC):
            _last_push_time = d['date']
            return True

    return False
