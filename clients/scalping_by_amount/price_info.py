import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))


from morning_server import message
from clients.common import morning_client
import numpy as np
from scipy.signal import find_peaks, peak_prominences

YCLOSE_MARK = 1
NORMAL_MARK = 2
CURRENT_MARK = 3
VI_MARK = 4
TODAY_OPEN_MARK = 5


def get_immediate_sell_price(ba_tick, all_qty):
    prices = [ba_tick['first_bid_price'], ba_tick['second_bid_price'],
                ba_tick['third_bid_price'], ba_tick['fourth_bid_price'],
                ba_tick['fifth_bid_price']]
    remain = [ba_tick['first_bid_remain'], ba_tick['second_bid_remain'],
                ba_tick['third_bid_remain'], ba_tick['fourth_bid_remain'],
                ba_tick['fifth_bid_remain']]
    for i, r in enumerate(remain):
        all_qty -= r
        if all_qty <= 0:
            return prices[i]
    return 0

def upper_available_empty_slots(slots):
    available_slots = []
    start_count = False

    for i in range(len(slots[0])):
        if start_count:
            if slots[1][i] == VI_MARK:
                break
            available_slots.append(slots[0][i])
        else:
            if slots[1][i] == CURRENT_MARK:
                start_count = True
    return available_slots


def get_price_unit_distance(low_price, high_price, is_kospi):
    if low_price >= high_price or low_price == 0 or high_price == 0:
        return 100 # abnormal price
    count = 0
    while low_price < high_price:
        count += 1
        unit = get_ask_bid_price_unit(low_price, is_kospi)
        low_price += unit
    return count

def get_ask_bid_price_unit(price, is_kospi):
    market_type = (message.KOSPI if is_kospi else message.KOSDAQ)
    return morning_client.get_ask_bid_price_unit(market_type, price)


def create_slots(yesterday_close, current_price, today_open, is_kospi):
    market_type = (message.KOSPI if is_kospi else message.KOSDAQ)
    bottom_price = int(yesterday_close * 0.7)
    top_price = int(yesterday_close * 1.3)

    bottom_ask_bid_unit = morning_client.get_ask_bid_price_unit(market_type, bottom_price)
    start_from = int(bottom_price / bottom_ask_bid_unit) * bottom_ask_bid_unit + bottom_ask_bid_unit
    vi_prices = _get_vi_prices(today_open, market_type)

    ask_bid_list = [[], []]
    while start_from < top_price:
        ask_bid_unit = morning_client.get_ask_bid_price_unit(market_type, start_from)
        ask_bid_list[0].append(start_from)

        if start_from == current_price:
            ask_bid_list[1].append(CURRENT_MARK)
        elif start_from in vi_prices:
            ask_bid_list[1].append(VI_MARK)
        elif start_from == yesterday_close:
            ask_bid_list[1].append(YCLOSE_MARK)
        elif start_from == today_open:
            ask_bid_list[1].append(TODAY_OPEN_MARK)
        else:
            ask_bid_list[1].append(NORMAL_MARK)
        start_from += ask_bid_unit
    return ask_bid_list


def _get_vi_prices(open_price, market_type):
    top_vi_prices = [open_price * 1.1, open_price * 1.2]
    bottom_vi_prices = [open_price * 0.8, open_price * 0.9]
    vi_list = []
    for vp in top_vi_prices:
        ask_bid_unit = morning_client.get_ask_bid_price_unit(market_type, vp)
        vi_list.append(int(vp / ask_bid_unit) * ask_bid_unit)

    for vp in bottom_vi_prices:
        ask_bid_unit = morning_client.get_ask_bid_price_unit(market_type, vp)
        vi_list.append(int(vp / ask_bid_unit) * ask_bid_unit + ask_bid_unit)
    return vi_list


def create_order_sheet(price_slots, all_qty):
    order_sheet = []
    order_qty = all_qty
    divider = all_qty / len(price_slots)
    if divider < 1:
        for p in price_slots:
            if order_qty <= 0:
                break
            order_qty -= 1
            order_sheet.append((p, 1))
    else:
        balancer = 0
        for i, p in enumerate(price_slots):
            if order_qty <= 0:
                break

            if i == len(price_slots) - 1:
                q = order_qty
            else:
                q = int(divider+balancer)
                balancer = divider + balancer - q
            order_qty -= q        
            order_sheet.append((p, q))
    return order_sheet


def _calculate(x):
    peaks, _ = find_peaks(x, distance=2)
    prominences = peak_prominences(x, peaks)[0]

    peaks = np.extract(prominences > x.mean() * 0.004, peaks)
    prominences = np.extract(prominences > x.mean() * 0.004, prominences)
    return peaks, prominences


def moving_average(data_set, periods=3):
    weights = np.ones(periods) / periods
    return np.convolve(data_set, weights, mode='valid')


def get_peaks(sec_price_list):
    if len(sec_price_list) < 3:
        return []
    ma = moving_average(np.array(sec_price_list))
    peaks, _ = _calculate(ma)
    return peaks


if __name__ == '__main__':
    l = create_slots(9000, 9500, 9100, False)
    # 9100 today open -> 10% -> 1010 VI, 20% -> 9100 + 1820 = 10920
    for i in range(len(l[0])):
        if l[1][i] != 2:
            print(l[0][i], l[1][i])

    print('available', upper_available_empty_slots(l))
