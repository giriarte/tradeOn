import yfinance as yf
# scripts/main.py
import sys
import os
import plotly.graph_objects as go
import numpy as np

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from indicators.rsi import RSI
from indicators.nRedCandles import NRedCandles
from strategies.strategy import TradeStrategy
from strategies.position import Position
from indicators.constants import ( 
    CLOSE_COLUMN,
    OPEN_COLUMN,
    N_CANDLES_LENGTH,
    N_CANDLES_OPERATION,
    RSI_LENGTH,
    RSI_BUY_THRESHOLD,
    RSI_SELL_THRESHOLD
)

def pointpos(x, xsignal):
    if x[xsignal]==2:
        return x['High']+1e-4
    elif x[xsignal]==1:
        return x['Low']-1e-4
    else:
        return np.nan

def plot_with_signal(dfpl):
    fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
                    open=dfpl[OPEN_COLUMN],
                    high=dfpl['High'],
                    low=dfpl['Low'],
                    close=dfpl[CLOSE_COLUMN])])

    fig.update_layout(
        autosize=False,
        width=1000,
        height=800, 
        paper_bgcolor='black',
        plot_bgcolor='black')
    fig.update_xaxes(gridcolor='black')
    fig.update_yaxes(gridcolor='black')
    fig.add_scatter(x=dfpl.index, y=dfpl['pointpos'], mode="markers",
                    marker=dict(size=8, color="MediumPurple"),
                    name="Signal")
    fig.show()


def plotResults(data):
    data['pointpos'] = data.apply(lambda row: pointpos(row,"strategy_output"), axis=1)
    plot_with_signal(data)

strategy_config = {
    RSI_LENGTH: 10,
    RSI_BUY_THRESHOLD: 30,
    RSI_SELL_THRESHOLD: 70,
    N_CANDLES_LENGTH: 3,
    N_CANDLES_OPERATION: 1
}

should_plot = True
raw_data = yf.download(tickers='BTC-USD', period='1y', interval='1d')
raw_data.columns = [col[0] for col in raw_data.columns]

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
raw_data["strategy_output"] = strategy_output

if (should_plot):
    plotResults(raw_data)

