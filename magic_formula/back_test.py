import tushare as ts
import pandas as pd

zz500 = ts.get_zz500s()
profits = ts.get_profit_data(2018,1)
profits = profits[['code', 'roe']]
profits = profits.set_index(['code'])
basics = ts.get_stock_basics()
basics = basics[['pe', 'name', 'industry']]

joined = zz500.join(profits).join(basics)
print(joined)