import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import timedelta

from morning_server import stock_api
from utils import time_converter
from morning.pipeline.converter import dt

def profit_price(arr):
    new_arr = []
    start_price = arr[0]
    for v in arr:
        new_arr.append((v - start_price) / start_price * 100)
    return new_arr


def save(message_reader, peak_data, data, start_time, until_time, matched_data):
    price_array, date_array, volume_array_old, price_average = data
    code = peak_data['code']

    volume_array = []
    matched_data_price_array = []
    matched_data_date_array = []
    matched_data_volume_array = []
    titles = ['comparision', peak_data['code']]

    current_volume = 0

    for v in volume_array_old:
        volume_array.append(v - current_volume)
        current_volume = v

    for m in matched_data:
        # before min data A087010 2018-01-02 find bug fix
        current_volume = 0
        min_data = stock_api.request_stock_minute_data(message_reader, 
                                                            m['code'], 
                                                            m['from_date'].date(), m['until_date'].date())
        if len(min_data) == 0:
            print('SAVE NO MIN DATA', code, m['from_date'], m['until_date'])
            continue
        min_data_c = []
        for md in min_data:
            min_data_c.append(dt.cybos_stock_day_tick_convert(md))

        min_data_price_array = [(mdata['lowest_price'] + mdata['close_price'] + mdata['highest_price'])/3 for mdata in min_data_c]
        min_data_date_array = []
        min_data_volume_array = []
        for mdata in min_data_c:
            min_data_volume_array.append(mdata['volume'])
            tc = time_converter.intdate_to_datetime(mdata['0']).date()
            if tc == m['from_date'].date():
                min_data_date_array.append(
                    date_array[0].replace(hour=int(mdata['time'] / 100), minute=int(mdata['time'] % 100)))
            else:
                min_data_date_array.append(
                    date_array[-1].replace(hour=int(mdata['time'] / 100), minute=int(mdata['time'] % 100)))
        
        matched_data_price_array.append(min_data_price_array)
        matched_data_date_array.append(min_data_date_array)
        matched_data_volume_array.append(min_data_volume_array)
        titles.append(m['code'] + m['from_date'].strftime('%Y%m%d-') + m['until_date'].strftime('%Y%m%d'))


    fig = make_subplots(rows=len(matched_data_price_array) + 2, cols=1, shared_xaxes=True, specs=[[{"secondary_y": True}]] * (len(matched_data_price_array) + 2), subplot_titles=titles)
    fig.add_trace(go.Scatter(x=date_array, y=profit_price(price_array), line=dict(color='black', width=2)), row=1, col=1)
    for i, data in enumerate(matched_data_price_array):
        fig.add_trace(go.Scatter(x=matched_data_date_array[i], y=profit_price(matched_data_price_array[i]), line=dict(width=1), opacity=0.8), row=1, col=1)
    fig.update_xaxes(type='category', tickformat='%H%M', row=1, col=1)

    fig.add_trace(go.Scatter(x=date_array, 
                                y=price_array, 
                                name=code, line=dict(color='black', width=1)), secondary_y=False, row=2, col=1)
    fig.add_trace(go.Scatter(x=date_array,
                                y=price_average, line=dict(color='green')), secondary_y=False, row=2, col=1)
    fig.add_trace(go.Bar(x=date_array, y=volume_array), row=2, col=1, secondary_y=True)
    fig.update_xaxes(type='category', tickformat='%H%M', row=2, col=1)
    fig.update_yaxes(title_text='price', secondary_y=False, row=2, col=1)
    fig.update_yaxes(title_text='volume', secondary_y=True, row=2, col=1)
    for i, data in enumerate(matched_data_price_array):
        fig.add_trace(go.Scatter(x=matched_data_date_array[i], y=data), row=i+3, col=1, secondary_y=False)
        fig.add_trace(go.Bar(x=matched_data_date_array[i], y=matched_data_volume_array[i]), row=i+3, col=1, secondary_y=True)
        fig.update_xaxes(type='category', tickformat='%H%M', row=i+3, col=1)
    shapes = [dict(x0=until_time, x1=until_time, y0=0, y1=1, xref='x', yref='paper', line_width=2)]
    annotations = []
    for p in peak_data['peak'][1:-1]:
        c = 'orange' if p['type'] == 1 else 'LightSeaGreen'
        annotations.append(
            go.layout.Annotation(x=p['time'], y=p['price'], text=('t' if p['type'] == 1 else 'b'), xref='x2', yref='y3', showarrow=True, arrowhead=7)
        )
        #shapes.append(dict(type='circle', x0=p['time'] - timedelta(minutes=5), x1=p['time'] + timedelta(minutes=5), y0=p['price'] - (p['price'] * 0.01), y1=p['price'] + (p['price'] * 0.01), xref='x2', yref='y2', line_color=c)) 


    fig.update_layout(title=code + '_' + start_time.strftime('%Y%m%d'), shapes=shapes, annotations=annotations, yaxis_tickformat='d', autosize=True, width=1920, height=(len(matched_data_price_array) + 2)* 300)
    #print(fig)
    fig.write_html(code + '_' + until_time.strftime('%Y%m%d%H%M_') + str(len(peak_data['peak'])) + '.html', auto_open=False)
    print('save done', code + '_' + until_time.strftime('%Y%m%d%H%M_') + str(len(peak_data['peak'])) + '.html')
