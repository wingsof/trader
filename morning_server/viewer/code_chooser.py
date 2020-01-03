from datetime import date, timedelta, datetime
from morning_server import stock_api
from morning_server import message


def get_candidate_code(market, yesterday, message_reader):
    # message.KOSPI or message.KOSDAQ
    market_code = stock_api.request_stock_code(message_reader, market)
    past_datas = []
    candidates = []
    for i, code in enumerate(market_code):
        past_data = stock_api.request_stock_day_data(message_reader, code, yesterday, yesterday)
        if len(past_data) == 1:
            data = past_data[0]
            data['code'] = code
            past_datas.append(data)
        else:
            print('No DATA or over size', code)
        print('Code Day Data', f'{i}/{len(market_code)}')

    past_datas = sorted(past_datas, key=lambda x: x['7'], reverse=True)
    past_datas = past_datas[:150]
    for data in past_datas:
        if data['9'] > data['8']:
            candidates.append(data['code'])
            
    return candidates  
