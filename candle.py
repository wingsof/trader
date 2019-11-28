
import plotly.graph_objects as go

import pandas as pd
from datetime import datetime

df = pd.read_excel('sample_data/A000250.xlsx')
df = df.set_index('date')

minute_df = pd.DataFrame(columns = ['date', 'code', 'open', 'low', 'high', 'close', 'volume'])
c = 'A000250'
for name, group in df.groupby(pd.Grouper(freq='60s')):
    if len(group) > 0:
        minute_df = minute_df.append({'date':name, 'code': group['code'].iloc[0], 'open': group['current_price'].iloc[0],
                            'low': group['current_price'].min(), 'high': group['current_price'].max(),
                            'close': group['current_price'].iloc[-1], 'volume': group['volume'].sum()}, 
                            ignore_index = True)
    else:
        minute_df = minute_df.append({'date':name, 'code': c, 'open': 0,
                            'low': 0, 'high': 0,
                            'close': 0, 'volume': 0}, 
                            ignore_index = True)



fig = go.Figure(data=[go.Candlestick(x=minute_df['date'],
                open=minute_df['open'], high=minute_df['high'],
                low=minute_df['low'], close=minute_df['close'])])

print(type(fig))
fig.show()

