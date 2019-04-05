import tushare as ts
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

import signal
import sys

def signal_handler(sig, frame):
        print('You pressed Ctrl+C!')
        sys.exit(0)

test = ts.get_hist_data('300558')
test = reversed(test['close'].tolist()[:15])
Y = [ [y] for y in test ]
Y = np.array(Y)
X_tmp = [ [i] for i in range(15) ]
X = np.array(X_tmp)
print(X, Y)
reg = LinearRegression().fit(X, Y)
Y_pred = reg.predict(X)

plt.plot(X, Y)
plt.plot(X, Y_pred)
print((Y[-1][0] - Y_pred[-1][0]) / Y_pred[-1][0])

plt.show()

# signal.signal(signal.SIGINT, signal_handler)
# print('Press Ctrl+C')
# signal.pause()

