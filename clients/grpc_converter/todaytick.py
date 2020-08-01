from gevent import monkey; monkey.patch_all()
from pymongo import MongoClient
from datetime import datetime, timedelta
from clients.common import morning_client
from morning_server import message


_code_classification = {}
_code_info = {}  # key: code, value: [mark, price]

_today_list = {}
REFRESH_SEC = 180
_today_period_list = {}
_last_push_time = None


def set_code_classification(code, is_kospi):
    if code not in _code_classification:
        _code_classification[code] = is_kospi


def get_code_classification(code):
    if code not in _code_classification:
        return False
    return _code_classification[code]


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
    _code_info.clear()


def handle_code_info(code, d):
    changed = False
    if code not in _code_info:
        yesterday_close = d['13'] - d['2']
        _code_info[code] = [False, yesterday_close, yesterday_close]
        changed = True
        
    open_price = d['4']
    if open_price > 0:
        if _code_info[code][1] == _code_info[code][2]:
            _code_info[code][1] = open_price
            changed = True

        if d['20'] == 49:
            _code_info[code][0] = True
        elif d['20'] == 50:
            if _code_info[code][0]:
                _code_info[code][0] = False
                _code_info[code][1] = d['13']
                changed = True
    else: # already set close
        pass


def get_vi_prices(code):
    vi_prices = []
    if code in _code_info:
        start_price = _code_info[code][1]
        price = start_price
        start_target = 10.0
        while price <= _code_info[code][2] * 1.3:
            unit = morning_client.get_ask_bid_price_unit((message.KOSPI if _code_classification[code] else message.KOSDAQ), price)
            price += unit
            if (price - start_price) / start_price * 100.0 >= start_target:
                start_target += 10.0
                vi_prices.append(price) 

        price = start_price
        start_target = -10.0
        while price >= _code_info[code][2] * 0.7:
            unit = morning_client.get_ask_bid_price_unit((message.KOSPI if _code_classification[code] else message.KOSDAQ), price - 1)
            price -= unit
            if (price - start_price) / start_price * 100.0 <= start_target:
                start_target -= 10.0
                vi_prices.append(price)

    return vi_prices



def handle_today_tick(code, d):
    global _today_list
    global _last_push_time

    handle_code_info(code, d)

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
