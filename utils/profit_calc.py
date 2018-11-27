import numpy as np

def get_avg_profit_by_day_data(df, buy_t, sell_t):
    bought = {'quantity': 0, 'price': 0}
    prev_close = 0
    initial_deposit = 1000000
    money = initial_deposit
    trade_count = 0

    for _, row in df.iterrows():
        buy_threshold = prev_close * buy_t
        sell_threshold = prev_close * sell_t

        if bought['quantity'] != 0 and row['low'] <= prev_close - sell_threshold:
            #money = (prev_close - sell_threshold) * bought['quantity']
            money = row['close'] * bought['quantity']
            money -= money * 0.003
            bought['quantity'] = 0
            trade_count += 1
        elif bought['quantity'] == 0 and prev_close != 0 and row['high'] >= prev_close + buy_threshold:
            bought['quantity'] = money / row['close']
            #bought['quantity'] = money / (prev_close + buy_threshold)
            money = 0

        prev_close = row['close']

    left = money if money != 0 else bought['quantity'] * prev_close
    return left / initial_deposit * 100, trade_count


def get_best_rate(df, reverse=False):
    buy_t_list = list(np.arange(0.01, 0.065, 0.001))
    sell_t_list = list(np.arange(0.01, 0.065, 0.001))
    buy_range = {}
    sell_range = {}
    for buy_t in buy_t_list:
        for sell_t in sell_t_list:
            if not reverse:
                profit, trade_count = get_avg_profit_by_day_data(df, buy_t, sell_t)
            else:
                profit, trade_count = get_avg_short_profit_by_day_data(df, buy_t, sell_t)

            if trade_count == 0: continue
            if buy_t in buy_range:
                buy_range[buy_t].extend([profit])
            else:
                buy_range[buy_t] = [profit]

            if sell_t in sell_range:
                sell_range[sell_t].extend([profit])
            else:
                sell_range[sell_t] = [profit]
    sorted_by_buy = sorted(buy_range.items(), key=lambda kv: sum(kv[1]) / len(kv[1]), reverse=True)
    sorted_by_sell = sorted(sell_range.items(), key=lambda kv: sum(kv[1]) / len(kv[1]), reverse=True)
    
    # when have a warning, close, high and low all values are same (no trades at all)
    if len(sorted_by_buy) == 0:
        return 0.0, 0.0, 0.0

    b_avg = sum(sorted_by_buy[0][1]) / len(sorted_by_buy[0][1])
    s_avg = sum(sorted_by_sell[0][1]) / len(sorted_by_sell[0][1])
    return sorted_by_buy[0][0], sorted_by_sell[0][0], (b_avg + s_avg) / 2


def get_avg_short_profit_by_day_data(df, buy_t, sell_t):
    initial_deposit = 1000000
    bought = {'quantity': 0, 'price': 0, 'balance': 0}
    prev_close = 0
    money = initial_deposit
    trade_count = 0

    for _, row in df.iterrows():
        buy_threshold = prev_close * buy_t
        sell_threshold = prev_close * sell_t

        if bought['quantity'] != 0 and row['high'] >= prev_close + buy_threshold:
            money = (bought['price'] - row['close']) * bought['quantity'] + bought['balance']
            money -= money * 0.003
            bought['quantity'] = 0
            trade_count += 1
        elif bought['quantity'] == 0 and prev_close != 0 and row['low'] <= prev_close - sell_threshold:
            bought['quantity'] = money / row['close']
            bought['price'] = row['close']
            bought['balance'] = money
            money = 0

        prev_close = row['close']

    left = money if money != 0 else (bought['price'] - prev_close) * bought['quantity'] + bought['balance']
    return left / initial_deposit * 100, trade_count
