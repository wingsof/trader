def find_previous_cross_highest(past_data):
    index = -1
    for i, p in enumerate(past_data):
        if p['moving_average'] > p['close_price']:
            index = i
            break
    if index == -1:
        return 0

    before_cross_data = past_data[index:]
    index = -1
    for i, p in enumerate(before_cross_data):
        if p['moving_average'] < p['close_price']:
            index = i
            break

    if index == -1:
        return 0

    prices = []
    previous_cross_data = before_cross_data[index:]
    for p in previous_cross_data:
        if p['moving_average'] < p['close_price']:
            prices.append(p['close_price'])

    if len(prices) == 0:
        return 0
    return max(prices)



a = [
        {'moving_average': 100, 'close_price': 120},
        {'moving_average': 100, 'close_price': 110},
        {'moving_average': 100, 'close_price': 100},
        {'moving_average': 100, 'close_price': 90},
        {'moving_average': 100, 'close_price': 80},
        {'moving_average': 100, 'close_price': 100},
        {'moving_average': 100, 'close_price': 110},
        {'moving_average': 100, 'close_price': 120},
        {'moving_average': 100, 'close_price': 130},
        {'moving_average': 100, 'close_price': 140},
        {'moving_average': 100, 'close_price': 150},
        {'moving_average': 100, 'close_price': 90},
]

print(find_previous_cross_highest(a))
