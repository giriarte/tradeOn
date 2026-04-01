import pandas_ta as ta
import typing as t

from indicators.constants import ( 
    CLOSE_COLUMN,
    RSI_BUY_THRESHOLD,
    RSI_COLUMN,
    RSI_LENGTH,
    RSI_SELL_THRESHOLD,
    SIGNAL_BUY,
    SIGNAL_HOLD,
    SIGNAL_SELL
)
from .indicator import Indicator

class RSI(Indicator):
    """
    A class to calculate the Relative Strength Index (RSI) and generate
    a simple buy/sell signal based on defined thresholds.
    """

    def evaluate(self, data: t.Any, params: t.Optional[t.Dict[str, t.Any]] = None) -> int:
        """
        Calculates RSI and returns a signal based on thresholds.

        Args:
            data (pd.DataFrame): DataFrame containing financial data (must have a 'Close' column).
            params (dict): Dictionary containing RSI parameters:
                           'length': RSI lookback period (e.g., 14)
                           'buy_threshold': RSI level below which a Buy signal is generated (e.g., 30)
                           'sell_threshold': RSI level above which a Sell signal is generated (e.g., 70)

        Returns:
            int: 0 (Hold/Neutral), 1 (Buy), or 2 (Sell).
        """

        # Use instance parameters if none are provided
        current_params = params
        if (current_params is None):
            current_params = self.params

        # Ensure 'Close' column exists before calculating RSI
        if CLOSE_COLUMN not in data.columns:
            print("Error: DataFrame must contain a 'Close' column.")
            return 0
            
        # 1. Calculate RSI using parameters from the map
        rsi_length = current_params.get(RSI_LENGTH, 14) # Default to 14 if not provided
        data[RSI_COLUMN] = ta.rsi(data.Close, length=rsi_length)
        
        # Check if RSI calculation was successful (i.e., not all NaN)
        if data[RSI_COLUMN].empty or data[RSI_COLUMN].iloc[-1] is None:
            print("Not enough data for calculation or failure")
            return 0

        # 2. Extract thresholds and current RSI value
        current_rsi = data.RSI.iloc[-1]
        buy_threshold = float(current_params.get(RSI_BUY_THRESHOLD, 30))
        sell_threshold = float(current_params.get(RSI_SELL_THRESHOLD, 70))
        
        output = SIGNAL_HOLD

        # 3. Apply the trading logic
        if current_rsi <= buy_threshold:
            output = SIGNAL_BUY
        elif current_rsi >= sell_threshold:
            output = SIGNAL_SELL 
            
        return output
