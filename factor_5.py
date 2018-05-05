import tushare as ts
import numpy as np
from sklearn import datasets, neural_network, linear_model
import pandas as pd
from datetime import date

import statsmodels.api as sm
from statsmodels import regression

FREQUENCY = 15  # 调仓频率
SAMPLE_DAYS = 63  # 样本长度
STOCKS = 10   # 持仓数目
RF = 0.04  # 无风险收益

'''
Ri=ai+biRM+siE(SMB)+hiE(HML)+εi
Ri=ai+biRM+siE(SMB)+hiE(HML)+εi
其中
Ri=E(ri−rf)，指股票i比起无风险投资的期望超额收益率。
RM=E(rM−rf)，为市场相对无风险投资的期望超额收益率，
E(SMB)是小市值公司相对大市值公司股票的期望超额收益率，
E(HML)则是高B/M公司股票比起低B/M的公司股票的期望超额收益率，

而 εi 是回归残差项。
具体计算方法：
rf : 直接选用基准利率，例如0.04
RM : 选择一个股指（例如沪深300）的收益 - rf
SMB: 大盘股的平均收益率 - 小盘股的平均收益率
'''

def Compute():
    today = str(date.today())
    trade_cal = ts.trade_cal()
    test = trade_cal.query('calendarDate < @today and isOpen == 1')
    start = test.iloc[-60].calendarDate
    end = test.iloc[-1].calendarDate

    hs300_kdata = ts.get_k_data('hs300', start=start, end=end)
    HS300 = hs300_kdata['close'][:]
    HS300_DIFF = np.diff(np.log(HS300))
    RM = HS300_DIFF - RF / 252
    stocks = ts.get_stock_basics()
    # stocks = stocks.iloc[0:30]

    kdatas = None
    counter = 0
    for scode, stock in stocks.iterrows():
        kdata = ts.get_k_data(scode, start=start, end=end)
        if kdatas is None:
            kdatas = kdata
        else:
            kdatas = pd.concat([kdatas, kdata]) 
        counter += 1
        print(counter)
    kdatas['log_close_price'] = np.log(kdatas.close)
    kdatas = kdatas.reset_index(drop=True)
    kdatas['diffs'] = kdatas.groupby("code")['log_close_price'].diff()

    stocks = stocks[['name', 'outstanding', 'bvps', 'pb']]
    stocks['market_cap'] = stocks.outstanding * stocks.bvps * stocks.pb
    stocks['BTM'] = 1 / stocks.pb
    # stocks.sort_values(['BTM'])
    # stocks.sort_values(['market_cap'])

    length = len(stocks)
    head = int(length / 3)
    tail = int(length - length / 3)
    S_BTM = stocks.sort_values('BTM').index.get_values()[:head]
    L_BTM = stocks.sort_values('BTM').index.get_values()[tail:]
    S_MC = stocks.sort_values('market_cap').index.get_values()[:head]
    L_MC = stocks.sort_values('market_cap').index.get_values()[tail:]
    # print(avg_day_r[['000014', '300107']])
    # print(kdatas[kdatas.code.isin(L_BTM)])
    HML = kdatas[kdatas.code.isin(L_BTM)].groupby("date")["diffs"].mean() 
    - kdatas[kdatas.code.isin(S_BTM)].groupby("date")["diffs"].mean()
    # SMB=sum(df4[S].T)/len(S)-sum(df4[B].T)/len(B)
    # HML=sum(df4[H].T)/len(H)-sum(df4[L].T)/len(L)
    # print(kdatas[kdatas.code.isin(S_MC)])
    SMB = kdatas[kdatas.code.isin(S_MC)].groupby("date")["diffs"].mean() 
    - kdatas[kdatas.code.isin(L_MC)].groupby("date")["diffs"].mean()
    
    X = pd.DataFrame({"RM":RM,"SMB":SMB[1:],"HML":HML[1:]})
    X['constant'] = 1
    X = X.values


    # 对样本数据进行线性回归并计算ai
    scores = {}
    for scode, stock in stocks.iterrows():
        # t_stock = stocks[scode]
        Y = kdatas.query('code == @scode')['diffs'] - RF / 252
        Y = Y.values
        Y = Y[1:]

        if len(Y) == len(RM):
            results = regression.linear_model.OLS(Y, X).fit()
            # print(scode, results.params[3])
            scores[scode] = results.params[3]
            # model = linear_model.LinearRegression().fit(X, Y)
            # print(model.coef_)
    sorted_scores = sorted(scores.items(), key=lambda d: d[1])
    for scode, score in sorted_scores:
        print(scode, score)

def main():
 #    X = [[-0.05, 0.004, -0.05, 1],
 # [-0.07, 0.007, -0.07, 1],
 # [-0.03, 0.006, -0.02, 1],
 # [-0.02, 0.005, -0.01, 1]]
 #    Y = [-0.1057798,  -0.10515739, -0.07917688, -0.02072908]
 #    results = regression.linear_model.OLS(Y, X).fit()
 #    print(results.params)
    # model = linear_model.LinearRegression().fit(X, Y)
    # print(model.coef_)
    Compute()

if __name__ == '__main__':
  main()
