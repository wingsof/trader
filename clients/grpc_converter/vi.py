from gevent import monkey; monkey.patch_all()
from pymongo import MongoClient
from datetime import datetime, timedelta


_vi_list = []
_current_display_option = 0
START_STATIC = 755
START_DYNAMIC = 751
STOP_STATIC = 756
STOP_DYNAMIC = 752
# ALL : 0, STATIC: 1, DYNAMIC: 2


def get_vi(opt, catch_plus):
    global _current_display_option

    _current_display_option = opt
    code_list = []
    for v in _vi_list:
        if catch_plus and v[3] < 0.0:
            continue

        if _current_display_option == 0:
            code_list.append(v[0])
        elif _current_display_option == 1 and v[1]:
            code_list.append(v[0])
        elif _current_display_option == 2 and not v[1]:
            code_list.append(v[0])
    return code_list


def handle_vi(code, d):
    global _vi_list
    #print('handle alarm', d)
    display_dynamic = _current_display_option == 0 or _current_display_option == 2
    display_static = _current_display_option == 0 or _current_display_option == 1

    if d['1'] != 49 or (d['2'] != 101 and d['2'] != 201):
        return False

    if d['4'] == START_STATIC or d['4'] == START_DYNAMIC:
        profit_index = d['6'].index('괴리율:')
        if profit_index == -1:
            return False

        profit = float(d['6'][profit_index+4:profit_index+10])
        found = False
        for i, v in enumerate(_vi_list):
            if v[0] == code:
                found = True
                v[3] = profit
                v[2] = True
                break
        if not found:
            _vi_list.insert(0, [code, d['4'] == START_STATIC, True, profit])

        if (d['4'] == START_STATIC and display_static) or (d['4'] == START_DYNAMIC and display_dynamic):
            return True
    elif d['4'] == STOP_STATIC or d['4'] == STOP_DYNAMIC:
        found = False
        for i, v in enumerate(_vi_list):
            if v[0] == code:
                v[2] = False 
                found = True
                break
        if found:
            if (d['4'] == STOP_STATIC and display_static) or (d['4'] == STOP_DYNAMIC and display_dynamic):
                return True

    return False
