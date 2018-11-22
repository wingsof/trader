import numpy as np

def get_avg_profit_by_day_data(df, buy_t, sell_t):
    bought = {'quantity': 0, 'price': 0}
    prev_close = 0
    initial_deposit = 1000000
    money = initial_deposit
    trade_count = 0

    for index, row in df.iterrows():
        buy_threshold = prev_close * buy_t
        sell_threshold = prev_close * sell_t

        if bought['quantity'] is not 0 and row['low'] <= prev_close - sell_threshold:
            money = (prev_close - sell_threshold) * bought['quantity']
            money -= money * 0.003
            bought['quantity'] = 0
        elif bought['quantity'] is 0 and prev_close != 0 and row['high'] >= prev_close + buy_threshold:
            bought['quantity'] = money / (prev_close + buy_threshold)
            money = 0
            trade_count += 1

        prev_close = row['close']

    left = money if money is not 0 else bought['quantity'] * prev_close
    return left / initial_deposit * 100, trade_count


def get_best_rate(df):
    buy_t_list = list(np.arange(0.01, 0.065, 0.001))
    sell_t_list = list(np.arange(0.01, 0.065, 0.001))
    buy_range = {}
    sell_range = {}
    for buy_t in buy_t_list:
        for sell_t in sell_t_list:
            profit, trade_count = get_avg_profit_by_day_data(df, buy_t, sell_t)
            if trade_count is 0: continue
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
    b_avg = sum(sorted_by_buy[0][1]) / len(sorted_by_buy[0][1])
    s_avg = sum(sorted_by_sell[0][1]) / len(sorted_by_sell[0][1])
    return sorted_by_buy[0][0], sorted_by_sell[0][0], (b_avg + s_avg) / 2

