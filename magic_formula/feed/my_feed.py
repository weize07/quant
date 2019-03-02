import tushare as ts
import pandas as pd
import os
import argparse
from pyalgotrade.barfeed import membf
from pyalgotrade import bar
import datetime

DIR = os.path.dirname(os.path.abspath(__file__))

def parse_date(date):
    # This custom parsing works faster than:
    # datetime.datetime.strptime(date, "%Y-%m-%d")
    year = int(date[0:4])
    month = int(date[5:7])
    day = int(date[8:10])
    d = datetime.datetime(year, month, day)
    if len(date) > 10:
        h = int(date[11:13])
        m = int(date[14:16])
        t = datetime.time(h,m)
        ret = datetime.combine(d,t)
    else:
         ret = d  
    return ret


class MyFeed(membf.BarFeed):
    def __init__(self, frequency = bar.Frequency.DAY, maxLen=None):
        super(MyFeed, self).__init__(frequency, maxLen)
       
    def rowParser(self, ds, frequency=bar.Frequency.DAY):
        dt = parse_date(ds["date"])
        open = float(ds["open"])
        close = float(ds["close"])
        high = float(ds["high"])
        low = float(ds["low"])
        volume = float(ds["volume"])
        return bar.BasicBar(dt, open, high, low, close, volume, None, frequency)
   
    def barsHaveAdjClose(self):
        return False
   
    def addBarsFromCode(self, code, start, end, ktype="D", index=False, offline=False):
        frequency = bar.Frequency.DAY
        if ktype == "D":
            frequency = bar.Frequency.DAY
        elif  ktype == "W":
            frequency = bar.Frequency.WEEK
        elif ktype == "M":
            frequency = bar.Frquency.MONTH
        elif ktype == "5" or ktype == "15" or ktype == "30" or ktype == "60":
            frequency = bar.Frequency.MINUTE
    
        cfile = os.path.join(DIR, 'cache', '%s_%s_%s_%s.csv' % (code, ktype, start, end))
        if offline and os.path.exists(cfile):
            ds = pd.read_csv(index_col=0)
        else:
            ds = ts.get_k_data(code = code, start = start, end = end, ktype = ktype, index = index)
            ds.to_csv(cfile)
        bars_ = []
        for i in ds.index:
            bar_ = self.rowParser(ds.loc[i], frequency)
            bars_.append(bar_)
        self.addBarsFromSequence(code, bars_)

    def getStocks(self, scope='zz500', offline=False):
        if scope == 'zz500':
            sfile = os.path.join(DIR, 'cache', '%s_stocks.csv' % scope)
            if offline and os.path.exists(sfile):
                universe = pd.read_csv(sfile, index_col=0)
            else:
                universe = ts.get_zz500s()
                universe.to_csv(sfile)
            return universe
        return None

    def addBars(self, start, end, scope='zz500', offline=False):
        universe = self.getStocks(scope, offline)
        for index, stock in universe.iterrows():
            self.addBarsFromCode(str(stock.code), start, end)
            break



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--offline', action='store_true',
                        help='Download from tushare or read from local cache(if exist).')
    parser.add_argument('--scope', dest='scope', type=str, 
                        default='zz500')
    start_date = '2018-01-01'
    end_date = '2018-02-01'
    args = parser.parse_args()
    feed = MyFeed()
    feed.addBars(start_date, end_date, args.scope, args.offline)

