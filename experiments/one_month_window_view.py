import pandas as pd
import matplotlib.pyplot as plt

short_data = pd.read_excel('short.xlsx')
long_data = pd.read_excel('long.xlsx')
short_data = short_data.set_index('date')
long_data = long_data.set_index('date')
ax = short_data.plot(color='blue', alpha=0.2)
long_data.plot(ax=ax, color='red', alpha=0.2)
plt.show()