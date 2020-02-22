from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))
from datetime import date, datetime, time, timedelta
from pymongo import MongoClient
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from morning_server import message
from configs import db
from clients.common import morning_client
from morning.back_data import holidays
from morning.pipeline.converter import dt


def get_tick_data(code, today, db_collection):
    from_datetime = datetime.combine(today, time(0,0))
    until_datetime = datetime.combine(today + timedelta(days=1), time(0,0))
    data = list(db_collection[code].find({'date': {'$gte': from_datetime, '$lte': until_datetime}}))
    converted_data = []
    for td in data:
        if code.endswith(message.BIDASK_SUFFIX):
            converted = dt.cybos_stock_ba_tick_convert(td)
        else:
            converted = dt.cybos_stock_tick_convert(td)
        converted_data.append(converted)
    return converted_data


def filter_in_market_tick(tick_data):
    index = 0
    for i, d in enumerate(tick_data):
        if d['market_type'] == dt.MarketType.IN_MARKET:
            index = i
            break
    # remove pre market summary tick (index+1)
    return tick_data[index+1:]


def filter_in_market_ba_tick(tick_data, t):
    index = 0
    for i, d in enumerate(tick_data):
        if d['date'] > t:
            index = i
            break
    return tick_data[index:]


def get_yesterday_amount_rank(today):
    market_code = morning_client.get_market_code()
    yesterday = holidays.get_yesterday(today)
    yesterday_list = []
    for progress, code in enumerate(market_code):
        print('collect yesterday data', f'{progress+1}/{len(market_code)}', end='\r')
        data = morning_client.get_past_day_data(code, yesterday, yesterday)
        if len(data) == 1:
            data = data[0]
            data['code'] = code
            yesterday_list.append(data)
    print('')
    yesterday_list = sorted(yesterday_list, key=lambda x: x['amount'], reverse=True)
    # For testing
    yesterday_list = yesterday_list[:100]
    return yesterday_list


def get_one_min_tick_quantity(tick_data, current_datetime):
    from_datetime = current_datetime - timedelta(seconds=60)
    data = list(filter(lambda x: from_datetime <= x['date'] <= current_datetime, tick_data)) 
    if len(data) > 0:
        return data[-1]['cum_buy_volume'] - data[0]['cum_buy_volume'], data[-1]['cum_sell_volume'] - data[0]['cum_sell_volume'], data

    return 0, 0, data


def get_one_min_ba_tick_quantity(ba_tick_data, current_datetime):
    from_datetime = current_datetime - timedelta(seconds=60)
    data = list(filter(lambda x: from_datetime <= x['date'] <= current_datetime, ba_tick_data)) 
    bid_volume = 0
    ask_volume = 0
    if len(data) > 0:
        for d in data:
            bid_volume += (d['first_bid_remain'] + d['second_bid_remain'] + d['third_bid_remain'])
            ask_volume += (d['first_ask_remain'] + d['second_ask_remain'] + d['third_ask_remain'])
        return bid_volume / len(data), ask_volume / len(data)
    return 0, 0


def save_to_graph(code, datetime_arr, price_arr, buy_speed_arr, sell_speed_arr, amount_arr):
    fig = make_subplots(rows=2, cols=1, specs=[[{"secondary_y": True}]] * 2)
    fig.add_trace(go.Scatter(x=datetime_arr, y=price_arr, name='price'), row=1, col=1)
    fig.add_trace(go.Scatter(x=datetime_arr, y=buy_speed_arr, name='buy sp', line=dict(color='red')), row=1, col=1, secondary_y=True)
    fig.add_trace(go.Scatter(x=datetime_arr, y=sell_speed_arr, name='sell sp', line=dict(color='blue')), row=1, col=1, secondary_y=True)
    fig.add_trace(go.Bar(x=datetime_arr, y=amount_arr), row=2, col=1)
    fig.update_layout(title=code, yaxis_tickformat='d')
    fig.update_yaxes(title_text="<b>primary</b> price", secondary_y=False)
    fig.update_yaxes(title_text="<b>secondary</b> speed", secondary_y=True)
    fig.write_html(os.environ['MORNING_PATH'] + os.sep + 'output' + os.sep + code+'.html', auto_open=False)


def start_meause_speed(today):
    db_collection = MongoClient(db.HOME_MONGO_ADDRESS).trade_alarm
    yesterday_list = get_yesterday_amount_rank(today)
    for ydata in yesterday_list:
        tick_data = get_tick_data(ydata['code'], today, db_collection)
        ba_tick_data = get_tick_data(ydata['code'] + message.BIDASK_SUFFIX, today, db_collection)
        if len(tick_data) < 1000 or len(ba_tick_data) < 1000:
            print(ydata['code'], 'not enough tick data', 'tick', len(tick_data), 'ba', len(ba_tick_data))
            continue
        tick_data = filter_in_market_tick(tick_data)
        if len(tick_data) < 1000:
            print(ydata['code'], 'not enough filtered tick data', len(tick_data))
            continue
        ba_tick_data = filter_in_market_ba_tick(ba_tick_data, tick_data[0]['date'])

        if len(ba_tick_data) < 1000:
            print(ydata['code'], 'not enough filtered ba tick data', len(ba_tick_data))
            continue

        print('start', ydata['code'])
        current_datetime = datetime.combine(today, time(9,0,10))
        price_array = []
        buy_speed_array = []
        sell_speed_array = []
        amount_array = []
        datetime_array = []
        MAX_SPEED_LIMIT = 5

        while current_datetime < datetime.combine(today, time(15,20)):
            buy_quantity, sell_quantity, filter_tick_data = get_one_min_tick_quantity(tick_data, current_datetime)
            bid_avg, ask_avg = get_one_min_ba_tick_quantity(ba_tick_data, current_datetime)
            if buy_quantity == 0 or sell_quantity == 0 or bid_avg == 0 or ask_avg == 0:
                current_datetime += timedelta(seconds=10)
                continue
            price_array.append(filter_tick_data[-1]['current_price'])
            buy_speed = ask_avg / buy_quantity
            sell_speed = bid_avg / sell_quantity

            if buy_speed > MAX_SPEED_LIMIT:
                buy_speed = MAX_SPEED_LIMIT

            if sell_speed > MAX_SPEED_LIMIT:
                sell_speed = MAX_SPEED_LIMIT

            buy_speed_array.append(buy_speed)
            sell_speed_array.append(sell_speed)
            amount_array.append(filter_tick_data[-1]['cum_amount'] - filter_tick_data[0]['cum_amount'])
            datetime_array.append(current_datetime)

            current_datetime += timedelta(seconds=10)
        save_to_graph(ydata['code'], datetime_array, price_array, buy_speed_array, sell_speed_array, amount_array)


if __name__ == '__main__':
    TODAY = date(2020, 2, 21)
    start_meause_speed(TODAY)
