# Trader fixed SL and TP
from backtesting import Strategy, Backtest
import yfinance as yf
import sys
import pandas as pd
import os
import numpy as np
import pandas_ta as ta

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from strategies.built_in_strategies.threeGreenCandlesRsi import ThreeGreenCandlesRsi
from utils.positionUtils import getTradeSize

# raw_data = yf.download(tickers='BTC-USD', period='1y', interval='1d')
# raw_data.columns = [col[0] for col in raw_data.columns]

raw_data = []

# To simulate 10x leverage (10% margin requirement)
LEVERAGE = 1
REQUIRED_MARGIN = 1 / LEVERAGE

def STRATEGY():
    test_strategy = ThreeGreenCandlesRsi("ThreeGreenCandlesRsi",
                                         ThreeGreenCandlesRsi.baseIndicators,
                                         ThreeGreenCandlesRsi.categoryAPosition,
                                         brokerId="test_broker",
                                         symbols=ThreeGreenCandlesRsi.symbols,
                                         candleInterval=ThreeGreenCandlesRsi.candleInterval)

    # Iterate through the data frame and append the strategy_output column
    strategy_output = [0]*len(raw_data)
    for i in range(0,len(raw_data)):
        df = raw_data[0 : i + 1]
        strategy_position_output= test_strategy.evaluate(df)
        if (strategy_position_output):
            strategy_output[i] = strategy_position_output.type
        else:
            strategy_output[i] = None
    return strategy_output

class BaseBacktestingStrat(Strategy): 
    rsi_window = 16
    def init(self):
        super().init()
        self.signal1 = self.I(STRATEGY)
        self.ratio = 1
        self.risk_perc = 0.0004
        # self.I() registers the indicator for the plotting engine
        # It takes: (function, data, additional_params)
        self.rsi = self.I(lambda x: ta.rsi(pd.Series(x), length=self.rsi_window), self.data.Close)

    def next(self):
        super().next() 

        # 1. Check if we already have an open position
        # If a position exists, we skip the rest of the logic for this candle
        if self.position:
            return
        
        tradeSize = getTradeSize(150000, self.data.Close[-1], LEVERAGE)
        if self.signal1==1:
            sl1 = self.data.Close[-1] - self.data.Close[-1]*self.risk_perc
            tp1 = self.data.Close[-1] + (self.data.Close[-1]*self.risk_perc)*self.ratio
            self.buy(size = tradeSize, sl=sl1, tp=tp1)
        elif self.signal1==2:
            sl1 = self.data.Close[-1] + self.data.Close[-1]*self.risk_perc
            tp1 = self.data.Close[-1] - (self.data.Close[-1]*self.risk_perc)*self.ratio
            self.sell(size = tradeSize, sl=sl1, tp=tp1)

data_path = os.path.abspath('tests\\historicalData5m\\fxify')
    
if not os.path.isdir(data_path):
    raise FileNotFoundError(f"Directory not found: {data_path}")

result_summary = []

for filename in os.listdir(data_path):
    # Check if the file ends with .csv
    if filename.endswith('.csv'):
        file_path = os.path.join(data_path, filename)
        
        print(f"Reading file: {filename}")

        raw_data = pd.read_csv(file_path, index_col=0, parse_dates=True)
        raw_data.index = pd.to_datetime(raw_data.index, format="%d.%m.%Y %H:%M:%S.%f")
        #raw_data.index = pd.to_datetime(raw_data.index, format="%Y-%m-%d %H:%M")
        raw_data['Open'] = pd.to_numeric(raw_data['Open'], errors='coerce')
        raw_data['Close'] = pd.to_numeric(raw_data['Close'], errors='coerce')
        raw_data['High'] = pd.to_numeric(raw_data['High'], errors='coerce')
        raw_data['Low'] = pd.to_numeric(raw_data['Low'], errors='coerce')
    
        # Drop rows where the values failed to convert (was a bad string)
        raw_data.dropna(subset=['Open'], inplace=True)
        raw_data.dropna(subset=['Close'], inplace=True)
        raw_data.dropna(subset=['High'], inplace=True)
        raw_data.dropna(subset=['Low'], inplace=True)

        print(f"read {len(raw_data)} rows.")

        # raw_data = yf.download(tickers='BTC-USD', period='1y', interval='1d')
        # raw_data.columns = [col[0] for col in raw_data.columns]
    
        # Uncomment this line to visualize the results properly. Plot library will not produce expected results for more than 10000 rows.
        raw_data = raw_data[0 : 20000]

        bt = Backtest(raw_data, BaseBacktestingStrat, cash=10000000, commission=.0001, margin=REQUIRED_MARGIN)
        stat = bt.run()
        print(stat)
        print(stat._trades)
        plotfilename = os.path.join("plots", filename)
        bt.plot(filename=plotfilename, resample=False)

        file_stats = {
            'filename': filename,
            'Return perc': stat['Return [%]'],
            'Equity final': stat['Equity Final [$]'],
            '# Trades': stat['# Trades'],
            'Win Rate perc': stat['Win Rate [%]'],
            'Avg trade perc': stat['Avg. Trade [%]'],
            'Sharpe Ratio': stat['Sharpe Ratio'],
            'Calmar Ratio': stat['Calmar Ratio']
        }
        result_summary.append(file_stats)

summary_df = pd.DataFrame(result_summary)

print("\n--- Summary DataFrame ---")
print(summary_df)