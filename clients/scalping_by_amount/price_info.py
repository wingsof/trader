import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))


from morning_server import message
from clients.common import morning_client


YCLOSE_MARK = 1
NORMAL_MARK = 2
CURRENT_MARK = 3
VI_MARK = 4
TODAY_OPEN_MARK = 5


def upper_available_empty_slots(slots):
    slot_count = 0
    start_count = False
    for i in range(len(slots[0])):
        if start_count:
            if slots[1][i] != NORMAL_MARK:
                break
            slot_count += 1
        else:
            if slots[1][i] == CURRENT_MARK:
                start_count = True
    return slot_count


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


if __name__ == '__main__':
    l = create_slots(9000, 9500, 9100, False)
    # 9100 today open -> 10% -> 1010 VI, 20% -> 9100 + 1820 = 10920
    for i in range(len(l[0])):
        if l[1][i] != 2:
            print(l[0][i], l[1][i])

    print('available', upper_available_empty_slots(l))
