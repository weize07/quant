import tushare as ts
import numpy as np
from sklearn import datasets, neural_network, linear_model

FREQUENCY=15  # 调仓频率
SAMPLE_DAYS=63  # 样本长度
STOCKS=10   # 持仓数目

#8
#按照Fama-French规则计算k个参数并且回归，计算出股票的alpha并且输出
#输入：stocks-list类型； begin，end为“yyyy-mm-dd”类型字符串,rf为无风险收益率-double类型
#输出：最后的打分-dataframe类型
def FF (stocks, begin, end, rf):
    LoS=len(stocks)
    #查询三因子/五因子的语句
    q = query(
        valuation.code,
        valuation.market_cap,
        (balance.total_owner_equities/valuation.market_cap/100000000.0).label("BTM"),
        indicator.roe,
        balance.total_assets.label("Inv")
    ).filter(
        valuation.code.in_(stocks)
    )

    df = get_fundamentals(q,begin)

    #计算5因子再投资率的时候需要跟一年前的数据比较，所以单独取出计算
    ldf=get_fundamentals(q,getDay(begin,-252))
    # 若前一年的数据不存在，则暂且认为Inv=0
    if len(ldf)==0:
        ldf=df
    df["Inv"]=np.log(df["Inv"]/ldf["Inv"])


    # 选出特征股票组合
    S=df.sort('market_cap')['code'][:LoS/3]
    B=df.sort('market_cap')['code'][LoS-LoS/3:]
    L=df.sort('BTM')['code'][:LoS/3]
    H=df.sort('BTM')['code'][LoS-LoS/3:]
    W=df.sort('roe')['code'][:LoS/3]
    R=df.sort('roe')['code'][LoS-LoS/3:]
    C=df.sort('Inv')['code'][:LoS/3]
    A=df.sort('Inv')['code'][LoS-LoS/3:]

    # 获得样本期间的股票价格并计算日收益率
    df2 = get_price(stocks,begin,end,'1d')
    df3=df2['close'][:]
    df4=np.diff(np.log(df3),axis=0)+0*df3[1:]
    #求因子的值
    SMB=sum(df4[S].T)/len(S)-sum(df4[B].T)/len(B)
    HMI=sum(df4[H].T)/len(H)-sum(df4[L].T)/len(L)
    RMW=sum(df4[R].T)/len(R)-sum(df4[W].T)/len(W)
    CMA=sum(df4[C].T)/len(C)-sum(df4[A].T)/len(A)

    #用沪深300作为大盘基准
    dp=get_price('000300.XSHG',begin,end,'1d')['close']
    RM=diff(np.log(dp))-rf/252

    #将因子们计算好并且放好
    X=pd.DataFrame({"RM":RM,"SMB":SMB,"HMI":HMI,"RMW":RMW,"CMA":CMA})
    #取前g.NoF个因子为策略因子
    factor_flag=["RM","SMB","HMI","RMW","CMA"][:g.NoF]
    print factor_flag
    X=X[factor_flag]

    # 对样本数据进行线性回归并计算ai
    t_scores=[0.0]*LoS
    for i in range(LoS):
        t_stock=stocks[i]
        sample=pd.DataFrame()
        t_r=linreg(X,df4[t_stock]-rf/252,len(factor_flag))
        t_scores[i]=t_r[0]

    #这个scores就是alpha
    scores=pd.DataFrame({'code':stocks,'score':t_scores})
    return scores

def main():


if __name__ == '__main__':
  main()
