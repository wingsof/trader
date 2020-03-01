from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))

import pandas as pd
import os
import sys
from datetime import datetime, timedelta
from morning_server import message
from morning_server import stock_api
from morning.pipeline.converter import dt
from clients.common import morning_client
from configs import db
from pymongo import MongoClient
from clients.search_rank import tick_analysis
import os.path

OUT_BASE = os.environ['MORNING_PATH'] + os.sep + 'output' + os.sep + 'bjj_tick'


def search_tick(tick_data, price, qty):
    found = False
    tick_arr = []
    for td in tick_data:
        if td['current_price'] == price and td['volume'] == qty:
            tick_arr.append(td)
            found = True

    if found:
        return tick_arr

    for d in range(1, 10):
        for i, td in enumerate(tick_data[:-d]):
            vol = td['volume']
            rest_vol = 0
            amount = td['volume'] * td['current_price']
            for j in range(i+1, i+1+d):
                rest_vol += tick_data[j]['volume']
                amount += tick_data[j]['volume'] * tick_data[j]['current_price']

            if rest_vol + vol == qty:
                tick_arr.append(td)

                for j in range(i+1, i+1+d):
                    tick_arr.append(tick_data[j])

                return tick_arr
    return tick_arr


def get_tick_data(code, from_datetime, until_datetime, db_collection):
    data = list(db_collection[code].find({'date': {'$gte': from_datetime, '$lte': until_datetime}}))
    converted_data = []
    for td in data:
        converted = dt.cybos_stock_tick_convert(td)
        converted_data.append(converted)
    return converted_data


def create_directory(path):
    if not os.path.exists(path):
        os.mkdir(path)


def parse_row(r, code_df):
    d = r[0]
    d = d.replace(u'\xa0', u' ')
    d = '2020/' + d
    name = r[2]
    ttype = 1 if r[1] == '매수' else 0
    price = r[3]
    qty = r[4]
    search_time = datetime.strptime(d, '%Y/%m/%d %H:%M')
    code_s = code_df[code_df['name'] == name]['code']
    code = next(iter(code_s), None)
    return search_time, code, name, ttype, price, qty


def process_code(code_info, directory):
    if len(code_info['buy_datetime_arr']) == 0:
        code_info['buy_datetime_arr'].append(code_info['start_time'])

    if len(code_info['sell_datetime_arr']) == 0:
        code_info['sell_datetime_arr'].append(code_info['finish_time'])

    #print('tick analysis', code_info['code'], code_info['buy_datetime_arr'])
    tick_analysis.start_tick_analysis(code_info['code'],
                                        code_info['buy_datetime_arr'], code_info['sell_datetime_arr'], directory) 


if __name__ == '__main__':
    db_collection = MongoClient(db.HOME_MONGO_ADDRESS).trade_alarm
    code_df = pd.read_excel(os.environ['MORNING_PATH'] + os.sep +
                'clients' + os.sep + 'search_rank' + os.sep + 'code_name.xlsx')
    sheet_names = ['2-26']
    processed_code = ''

    for sn in sheet_names:
        create_directory(os.path.join(OUT_BASE, sn))
        df = pd.read_excel(
                os.environ['MORNING_PATH'] + os.sep +
                'sample_data' + os.sep + 'bjj_trading.xlsx',
                sheet_name=sn,
                header=None)
        trans_data = []
        code_dict = dict()  # key: code, buy_datetime_arr: [], sell_datetime_arr: [], qty: 0
        for index, row in df.iterrows():
            # 0: date, 1: buy/sell 2: name 3: price 4: quantity 5 : amount
            row_date, code, stock_name, ttype, price, qty = parse_row(row, code_df)
            print(code, stock_name, price, qty, row_date)
            if code == None:
                print('Cannot find code name', stock_name)
                trans_data.append({'date': row_date,
                                    'name': stock_name,
                                    'type': ttype,
                                    'price': price,
                                    'qty': qty,
                                    'code': 'Unknown',
                                    'etime': None,
                                    'flag': None})
                continue

            tick_data = get_tick_data(code, row_date, row_date + timedelta(seconds=60), db_collection)

            if code not in code_dict:
                code_dict[code] = {'code': code, 'buy_datetime_arr': [], 'sell_datetime_arr': [], 'qty': 0, 'start_time': None, 'finish_time': None, 'count': 0}
                if len(processed_code) == 0:
                    processed_code = code
                else:
                    if code != processed_code and code_dict[processed_code]['count'] > 1:
                        process_code(code_dict[processed_code], os.path.join(OUT_BASE, sn))
                        code_dict.pop(processed_code, None)
                        processed_code = code

            code_dict[code]['count'] += 1

            if len(tick_data) > 0:
                if code_dict[code]['start_time'] == None:
                    code_dict[code]['start_time'] = tick_data[0]['date']

                code_dict[code]['finish_time'] = tick_data[-1]['date']

                matched_ticks = search_tick(tick_data, price, qty)
                trans_data.append({'date': row_date,
                                    'name': stock_name,
                                    'type': ttype,
                                    'price': price,
                                    'qty': qty,
                                    'code': code,
                                    'etime': [m['date'] for m in matched_ticks],
                                    'flag': [m['buy_or_sell'] for m in matched_ticks]})
                if ttype == 1:
                    code_dict[code]['buy_datetime_arr'].extend([m['date'] for m in matched_ticks])
                else:
                    code_dict[code]['sell_datetime_arr'].extend([m['date'] for m in matched_ticks])
            else:
                print('Cannot find tick data', code)
                if code_dict[code]['start_time'] == None:
                    code_dict[code]['start_time'] = row_date

                code_dict[code]['finish_time'] = row_date

                trans_data.append({'date': row_date,
                                    'name': stock_name,
                                    'type': ttype,
                                    'price': price,
                                    'qty': qty,
                                    'code': code,
                                    'etime': None, 'flag': None})

        process_code(code_dict[processed_code], os.path.join(OUT_BASE, sn))
        pd.DataFrame(trans_data).to_excel(os.path.join(OUT_BASE, sn, sn + '.xlsx'))
        print('Done')

