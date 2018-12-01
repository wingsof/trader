

a = {}
balance = 14000
balance = balance / 10.

a['A00'] = [105, 0]
a['A01'] = [107, 100]
a['A02'] = [108, 200]
a['A03'] = [109, 300]
a['A04'] = [110, 400]
a['A05'] = [111, 500]

c = []
b = sorted(a.items(), key=lambda kv: kv[1][1])

default_price = 0
for i, v in b:
    if v[1] == 0 or default_price + v[1] > balance:
        continue
    
    default_price += v[1]
    c.append((i, v))

quantities = [1] * len(c)

def get_prices(item, q):
    prices = []
    for i, p in enumerate(item):
        prices.append(quantities[i] * p[1][1])
    return prices

def over_limit(item, q, limit):
    total = 0
    for i, s in enumerate(item):
        total += s[1][1] * q[i]
    if total > limit:
        return True

    return False

def add_quantity(item, q):
    qq = q.copy()
    p = get_prices(item, qq)

    index = p.index(min(p))
    qq[index] += 1

    if over_limit(item, qq, balance):
        return False
    else:
        q[:] = qq
        return True


while True:
    if not add_quantity(c, quantities):
        break

print(c)
print(quantities)
