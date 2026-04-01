import yfinance as yf
import sys
import os
import plotly.graph_objects as go
import numpy as np

# --- System Path Setup (Keep as is) ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- Imports (Keep as is) ---
from indicators.rsi import RSI
from indicators.nRedCandles import NRedCandles
from model.strategy import TradeStrategy
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

# --- Helper Functions (Keep as is) ---
def pointpos(x, xsignal):
    if x[xsignal] == 2:
        return x['High'] + 1e-4
    elif x[xsignal] == 1:
        return x['Low'] - 1e-4
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
    data['pointpos'] = data.apply(lambda row: pointpos(row, "strategy_output"), axis=1)
    plot_with_signal(data)

# ====================================================================
# --- NEW: Main Logic Function ---
# ====================================================================

def main(event, context):
    """
    Main execution function for the trading strategy simulation.
    """
    # 1. Configuration
    strategy_config = {
        RSI_LENGTH: 10,
        RSI_BUY_THRESHOLD: 30,
        RSI_SELL_THRESHOLD: 70,
        N_CANDLES_LENGTH: 3,
        N_CANDLES_OPERATION: 1
    }

    should_plot = True
    
    # 2. Data Download and Cleanup
    print("Downloading data...")
    raw_data = yf.download(tickers='BTC-USD', period='1y', interval='1d')
    # Clean up column names (e.g., ('Close', '') -> 'Close')
    raw_data.columns = [col[0] if isinstance(col, tuple) else col for col in raw_data.columns]
    
    # 3. Instantiate the Indicators and Strategy
    print("Instantiating strategy components...")
    rsi_indicator = RSI()
    nRedCandles_indicator = NRedCandles()

    rsi_3RedCandles_strategy = TradeStrategy()
    rsi_3RedCandles_strategy.baseIndicators = [nRedCandles_indicator, rsi_indicator]
    rsi_3RedCandles_strategy.categoryAPosition = Position()

    # 4. Strategy Iteration and Execution
    print("Executing backtest...")
    strategy_output = [0] * len(raw_data)
    
    # Start iteration after the period needed for initial indicators (e.g., 3 days)
    # The actual start should probably be based on the max length of your indicators.
    start_index = max(3, strategy_config.get(RSI_LENGTH, 10)) # Use max indicator length
    
    for i in range(start_index, len(raw_data)):
        # Pass the data up to the current bar (i+1 to include current bar)
        df = raw_data.iloc[0:i+1] 
        
        strategy_position_output = rsi_3RedCandles_strategy.evaluate(df, strategy_config)
        
        if strategy_position_output:
            # Store the type (e.g., 1 for Buy, 2 for Sell)
            strategy_output[i] = strategy_position_output.type
        else:
            strategy_output[i] = 0 # Use 0 instead of None for easier plotting/analysis
            
    raw_data["strategy_output"] = strategy_output
    print("Backtest complete.")

    # 5. Plotting Results
    if should_plot:
        print("Plotting results...")
        plotResults(raw_data)

# ====================================================================
# --- Standard Python Entry Point ---
# ====================================================================

if __name__ == "__main__":
    main('', '')