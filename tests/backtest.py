# Trader fixed SL and TP
from backtesting import Strategy, Backtest
import yfinance as yf
import sys
import os
import numpy as np

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from indicators.rsi import RSI
from indicators.nRedCandles import NRedCandles
from strategies.strategy import TradeStrategy
from strategies.position import Position

raw_data = yf.download(tickers='BTC-USD', period='1y', interval='1d')
raw_data.columns = [col[0] for col in raw_data.columns]

# To simulate 10x leverage (10% margin requirement)
LEVERAGE = 10 
REQUIRED_MARGIN = 1 / LEVERAGE

def STRATEGY():
    strategy_config = {
        'length': 10,
        'buy_threshold': 30,
        'sell_threshold': 70,
        'n_candles': 3,
        'n_candles_operation': 1
    }

    # 3. Instantiate the Indicators (rsi + 3 red candles)
    rsi_indicator = RSI()
    nRedCandles_indicator = NRedCandles()

    rsi_3RedCandles_strategy = TradeStrategy()
    rsi_3RedCandles_strategy.baseIndicators = [nRedCandles_indicator, rsi_indicator]
    rsi_3RedCandles_strategy.categoryAPosition = Position()

    # Iterate through the data frame and append the strategy_output column
    strategy_output = [0]*len(raw_data)
    for i in range(3,len(raw_data)):
        df = raw_data[0:i+1]
        strategy_position_output= rsi_3RedCandles_strategy.evaluate(df, strategy_config)
        if (strategy_position_output):
            strategy_output[i] = strategy_position_output.type
        else:
            strategy_output[i] = None
    return strategy_output

class MyCandlesStrat(Strategy):  
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
bt = Backtest(raw_data, MyCandlesStrat, cash=100000, commission=.02, margin=REQUIRED_MARGIN)

stat = bt.run()

print(stat)
bt.plot()