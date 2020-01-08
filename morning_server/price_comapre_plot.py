import plotly.graph_objects as go
from plotly.subplots import make_subplots

from morning_server import stock_api
from utils import time_converter


def save(message_reader, code, data, start_time, until_time, matched_data):
    price_array, date_array, volume_array = data

    matched_data_price_array = []
    matched_data_date_array = []
    for m in matched_data:
        print('before min data', m['code'], m['from_date'].date())
        # before min data A087010 2018-01-02 find bug fix
        min_data = stock_api.request_stock_minute_data(message_reader, 
                                                            m['code'], 
                                                            m['from_date'].date(), m['until_date'].date())
        print('after min data')
        if len(min_data) == 0:
            print('SAVE NO MIN DATA', code, m['from_date'], m['until_date'])
            continue
        min_data_price_array = [(mdata['lowest_price'] + mdata['close_price'] + mdata['highest_price'])/3 for mdata in min_data]
        min_data_date_array = []
        for mdata in min_data:
            tc = time_converter.datetime_to_intdate(mdata['0']).date()
            if tc == m['from_date'].date():
                min_data_date_array.append(
                    date_array[0].replace(hour=int(mdata['time'] / 100), minute=int(mdata['time'] % 100)))
            else:
                min_data_date_array.append(
                    date_array[-1].replace(hour=int(mdata['time'] / 100), minute=int(mdata['time'] % 100)))
        
        matched_data_price_array.append(min_data_price_array)
        matched_data_date_array.append(min_data_date_array)

    print('make plot starting')
    fig = make_subplots(rows=len(matched_data_price_array) + 1, cols=1)
    print('make plot starting')
    fig.add_trace(go.Scatter(x=date_array, 
                                y=price_array, 
                                name=code), row=1, col=1)

    for i, data in enumerate(matched_data_price_array):
        fig.add_trace(go.Scatter(x=matched_data_date_array[i], y=data), row=i+2, col=1)
    fig.update_layout(title=code + '_' + start_time.strftime('%Y%m%d'), yaxis_tickformat='d', autosize=False, width=1200, height=2400,)
    print('before write')
    fig.write_html(code + '_' + start_time.strftime('%Y%m%d') + '.html', auto_open=False)