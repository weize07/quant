# coding="utf8"
import os

from pyalgotrade import strategy
from feed import my_feed
from pyalgotrade import plotter
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross
from pyalgotrade.stratanalyzer import returns



class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, smaPeriod):
        super(MyStrategy, self).__init__(feed)
        self.__instrument = instrument
        self.__closed = feed[instrument].getCloseDataSeries()
        self.__ma = ma.SMA(self.__closed, smaPeriod)
        self.__position = None
       
    def getSMA(self):
        return self.__ma
   
    def onEnterLong(self, position):
        print("onEnterLong", position.getShares())
       
    def onEnterCanceled(self, position):
        self.__position = None
        print("onEnterCanceled", position.getShares())
       
    def onExitOk(self, position):
        self.__position = None
        print("onExitOk", position.getShares())
       
    def onExitCanceled(self, position):
        self.__position.exitMarket()
        print("onExitCanceled", position.getShares())
       
    def onBars(self, bars):
        if self.__position is None:
            if cross.cross_above(self.__closed, self.__ma) > 0:
                shares = int(self.getBroker().getCash() * 0.9 / bars[self.__instrument].getPrice())
                print("cross_above shares,", shares)
                # Enter a buy market order. The order is good till canceled.
                self.__position = self.enterLong(self.__instrument, shares, True)
        elif not self.__position.exitActive() and cross.cross_below(self.__closed, self.__ma) > 0:
            print("cross_below")
            self.__position.exitMarket()
           

    def getClose(self):
        return self.__closed


if __name__ == '__main__':
    code = "603019"
    feed = my_feed.MyFeed()
    feed.addBarsFromCode(code, start='2018-01-29',end='2018-04-04')

    # Evaluate the strategy with the feed's bars.
    myStrategy = MyStrategy(feed, code, 5)
    returnsAnalyzer = returns.Returns()
    myStrategy.attachAnalyzer(returnsAnalyzer)
    plt = plotter.StrategyPlotter(myStrategy)
    plt.getInstrumentSubplot(code).addDataSeries("SMA", myStrategy.getSMA())
    plt.getOrCreateSubplot("returns").addDataSeries("Simple returns", returnsAnalyzer.getReturns())

    myStrategy.run()

    myStrategy.info("Final portfolio value: $%.2f" % myStrategy.getResult())

    plt.plot()

