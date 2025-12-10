import pandas_ta as ta
import typing as t
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

        default_config = {
            'length': 10,
            'buy_threshold': 30,
            'sell_threshold': 70
        }
        
        current_params = default_config.copy()
        if params:
            current_params.update(params)

        # Ensure 'Close' column exists before calculating RSI
        if 'Close' not in data.columns:
            print("Error: DataFrame must contain a 'Close' column.")
            return 0
            
        # 1. Calculate RSI using parameters from the map
        rsi_length = current_params.get('length', 14) # Default to 14 if not provided
        data["RSI"] = ta.rsi(data.Close, length=rsi_length)
        
        # Check if RSI calculation was successful (i.e., not all NaN)
        if data["RSI"].empty or data["RSI"].iloc[-1] is None:
            print("Not enough data for calculation or failure")
            return 0

        # 2. Extract thresholds and current RSI value
        current_rsi = data.RSI.iloc[-1]
        buy_threshold = current_params.get('buy_threshold', 30)
        sell_threshold = current_params.get('sell_threshold', 70)
        
        output = 0

        # 3. Apply the trading logic
        if current_rsi <= buy_threshold:
            output = 1  # Buy Signal
        elif current_rsi >= sell_threshold:
            output = 2  # Sell Signal
            
        return output
