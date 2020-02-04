from sklearn.linear_model import LinearRegression
import numpy as np


def positive_slope(today, code_dict):
    candidates = []
    for progress, (code, v) in enumerate(code_dict.items()):
        print('positive slope', today, f'{progress+1}/{len(code_dict)}', end='\r')
        past_data = v['past_data']
        last_mavg = [d['moving_average'] for d in past_data[-10:]]
        X = np.arange(len(last_mavg)).reshape((-1,1))
        reg = LinearRegression().fit(X, np.array(last_mavg))
        if reg.coef_[0] > 0:
            candidates.append(code)
    print('')
    return candidates


def positive_cum_volume(today, code_dict):
    candidates = []
    cum_buy_codes = []
    for progress, (code, v) in enumerate(code_dict.items()):
        print('positive cum volume', today, f'{progress+1}/{len(code_dict)}', end='\r')
        past_data = v['past_data']
        yesterday_data = past_data[-1]

        if yesterday_data['cum_buy_volume'] > yesterday_data['cum_sell_volume']:
            candidates.append(code)
    print('')
    return candidates


def positive_yesterday_close_over_mavg(today, code_dict):
    candidates = []
    for progress, (code, v) in enumerate(code_dict.items()):
        print('positive yesterday close', today, f'{progress+1}/{len(code_dict)}', end='\r')
        past_data = v['past_data']
        yesterday_data = past_data[-1]

        if yesterday_data['moving_average'] > yesterday_data['close_price']:
            candidates.append(code)
    print('')
    return candidates


def higher_yesterday_amount(today, code_dict):
    candidates = []
    for progress, (code, v) in enumerate(code_dict.items()):
        print('higher yesterday amount', today, f'{progress+1}/{len(code_dict)}', end='\r')
        past_data = v['past_data']
        yesterday_data = past_data[-1]
        candidates.append({'code': code, 'amount': yesterday_data['amount']})
    candidates = sorted(candidates, key=lambda x: x['amount'], reverse=True)
    candidates = candidates[:150]
    print('')
    return [d['code'] for d in candidates]
