import tushare as ts
import pandas as pd

# universe = ts.get_zz500s()
# universe = universe.set_index(['code'])

universe = ts.get_hs300s()
universe = universe.set_index(['code'])

profits = ts.get_profit_data(2018,3)
profits = profits[['code', 'roe']]
profits = profits.set_index(['code'])

basics = ts.get_stock_basics()
basics = basics[['pe', 'industry']]

roe_index = universe.join(profits).sort_values(by=['roe'], ascending=False).reset_index(drop=False)
pe_index = universe.join(basics).sort_values(by=['pe'], ascending=True).reset_index(drop=False)

# roe_index.to_csv("roe_index.csv")
# pe_index.to_csv("pe_index.csv")

# roe_index = pd.read_csv('roe_index.csv')
# pe_index = pd.read_csv('pe_index.csv')
score = {}
name_industry = {}
for index, row in roe_index.iterrows():
    score[row['name']] = index
for index, row in pe_index.iterrows():
    score[row['name']] += index
    name_industry[row['name']] = row['industry']

score_list = [ (score[key], key) for key in score ]
score_list = sorted(score_list)
for s in score_list:
    print(s[0], s[1], name_industry[s[1]])


