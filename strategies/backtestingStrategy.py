# Trader fixed SL and TP
from backtesting import Strategy, Backtest
from backtesting.lib import plot_heatmaps
import yfinance as yf
import sys
import os
import numpy as np

from tests.backtest import STRATEGY

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from indicators.constants import N_CANDLES_LENGTH, N_CANDLES_OFFSET, N_CANDLES_OPERATION, RSI_BUY_THRESHOLD, RSI_LENGTH, RSI_SELL_THRESHOLD
from strategies.built_in_strategies.threeGreenCandlesRsi import ThreeGreenCandlesRsi


# raw_data = yf.download(tickers='BTC-USD', period='1y', interval='1d')
# raw_data.columns = [col[0] for col in raw_data.columns]

# To simulate 10x leverage (10% margin requirement)
# LEVERAGE = 10 
# REQUIRED_MARGIN = 1 / LEVERAGE

# rsiLength = 10
# rsiBuyThreshold = 30
# rsiSellThreshold = 70
# nCandlesLength = 3
# nCandlesOperation = 2
# nCandlesOffset = 1

# testParams = {
#     RSI_LENGTH: rsiLength,
#     RSI_BUY_THRESHOLD: rsiBuyThreshold,
#     RSI_SELL_THRESHOLD: rsiSellThreshold,
#     N_CANDLES_LENGTH: nCandlesLength,
#     N_CANDLES_OPERATION: nCandlesOperation,
#     N_CANDLES_OFFSET: nCandlesOffset
# } # Inidicators parameters



class BacktestingStrategy(Strategy):  
    # rsiLength = 10
    # rsiBuyThreshold = 30
    # rsiSellThreshold = 70
    # nCandlesLength = 3
    # nCandlesOperation = 2
    # nCandlesOffset = 1

    # testParams = {
    #     RSI_LENGTH: rsiLength,
    #     RSI_BUY_THRESHOLD: rsiBuyThreshold,
    #     RSI_SELL_THRESHOLD: rsiSellThreshold,
    #     N_CANDLES_LENGTH: nCandlesLength,
    #     N_CANDLES_OPERATION: nCandlesOperation,
    #     N_CANDLES_OFFSET: nCandlesOffset
    # } # Inidicators parameters

    def init(self):
        super().init()
        self.signal1 = self.I(STRATEGY)
        self.ratio = 1.5
        self.risk_perc = 0.08

    def next(self):
        super().next() 
        if self.signal1==1:
            sl1 = self.data.Close[-1] - self.data.Close[-1]*self.risk_perc
            tp1 = self.data.Close[-1] + (self.data.Close[-1]*self.risk_perc)*self.ratio
            self.buy(size = 1, sl=sl1, tp=tp1)
        elif self.signal1==2:
            sl1 = self.data.Close[-1] + self.data.Close[-1]*self.risk_perc
            tp1 = self.data.Close[-1] - (self.data.Close[-1]*self.risk_perc)*self.ratio
            self.sell(size = 1, sl=sl1, tp=tp1)
# bt = Backtest(raw_data, BacktestingStrategy, cash=100000, commission=.02, margin=REQUIRED_MARGIN)
# optimized_stats, heatmap = bt.optimize(
#     rsiLength=range(5, 15, 1),
#     rsiBuyThreshold=range(20, 40, 5),
#     rsiSellThreshold=range(60, 90, 5),
#     nCandlesLength=range(2, 5, 1),
#     nCandlesOperation=2,
#     nCandlesOffset=range(0, 3, 1),
#     maximize='Sharpe Ratio',
#     max_tries=30,
#     return_heatmap=True)

# print(optimized_stats)
# print("Parameters for best result: ", optimized_stats['_strategy'])
# plot_heatmaps(heatmap, agg='mean')

# stat = bt.run()
# print(stat)
# bt.plot()