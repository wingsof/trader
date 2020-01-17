import sys, os
import pandas as pd
from datetime import datetime



if len(sys.argv) < 2:
    print('Usage:', sys.argv[0], '[excel file]')
    sys.exit(1)

if not os.path.exists(sys.argv[1]):
    print('file not exist')
    sys.exit(1)

df = pd.read_excel(sys.argv[1])


# Test 1
t1_df = df[df['code'] == 'A017890']
assert(len(t1_df[t1_df['buy_date'] == datetime(2019, 4, 9)]) == 1)
assert(len(t1_df[t1_df['sell_date'] == datetime(2019, 4, 19)]) == 1)

t2_df = df[df['code'] == 'A010240']
t2_1 = t2_df[(t2_df['buy_date'] >= datetime(2019, 10, 1)) & (t2_df['buy_date'] <= datetime(2019, 11, 1))]
assert(len(t2_1) == 0)

t3_df = df[df['code'] == 'A032685']
t3_1 = t3_df[(t3_df['buy_date'] >= datetime(2019, 1, 1)) & (t3_df['buy_date'] <= datetime(2019, 2, 28))]
assert(len(t3_1) == 0)

t4_df = df[df['code'] == 'A089970']
t4_1 = t4_df[t4_df['buy_date'] == datetime(2019, 4, 4)]
t4_2 = t4_df[t4_df['sell_date'] == datetime(2019, 4, 5)]
assert(len(t4_1) == 1)
assert(len(t4_2) == 1)

t5_df = df[df['code'] == 'A048470']
t5_1 = t5_df[t5_df['buy_date'] == datetime(2019, 9, 16)]
t5_2 = t5_df[t5_df['sell_date'] == datetime(2019, 9, 23)]
assert(len(t5_1) == 1)
assert(len(t5_2) == 1)
print('Success')
