from gevent import monkey; monkey.patch_all()
from clients.grpc_converter import preload
import config


_today_data = {}
_ninethirty_codes = []


def clear_all():
    _today_data.clear()
    _ninethirty_codes.clear()


def get_ninethirty_codes():
    return _ninethirty_codes


def handle_tick(code, d):
    if preload.loading or preload.is_skip_ydata():
        return config.CAND_NONE

    if code in _today_data:
        if d['time'] > 930:
            amount = d['cum_amount'] * 10000 if preload.is_kospi(code) else d['cum_amount'] * 1000
            if amount >= _today_data[code]:
                _ninethirty_codes.append(code)
                del _today_data[code]
                return config.CAND_NINETHIRTY
    else:
        if d['time'] > 930:
            return config.CAND_NONE
        else:
            if preload.get_yesterday_amount[code] >= 2000000000:
                year_high = preload.get_yesterday_year_high(code)
                if year_high != 0 and preload.get_yesterday_close() >= year_high * 0.8:
                    _today_data[code] = preload.get_yesterday_amount[code]

    return config.CAND_NONE
