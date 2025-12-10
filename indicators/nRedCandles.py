import typing as t
import pandas as pd
from .indicator import Indicator

# Define the type alias for clarity
IndicatorParams = t.Dict[str, t.Any]

class NRedCandles(Indicator):
    """
    Indicator that generates a Buy signal (1) if the most recent N candles 
    are bearish (red, meaning Close < Open), and returns 0 otherwise.
    """

    def evaluate(self, data: t.Any, params: t.Optional[IndicatorParams] = None) -> int:
        """
        Calculates the N Red Candles Buy signal.

        Args:
            data (pd.DataFrame): DataFrame containing financial data (must have 'Open' and 'Close').
            params (Optional[Dict]): Dictionary containing 'n_candles' (int) 
                                     specifying the required number of consecutive red candles.
                                     
        Returns:
            int: 1 (Buy signal) or 0 (Hold/Neutral).
        """
        
        # 1. Parameter Handling (N)
        default_n = 3 # Default lookback if not provided

        n_candles_operation = 1 # Default operation is to buy, but it can be changed by parameter to 2 (sell)
        n_candles = default_n
        
        if params and 'n_candles' in params:
            n_candles = params['n_candles']
            
        if params and 'n_candles_operation' in params:
            n_candles_operation = params['n_candles_operation']
        
        # 2. Data Validation
        if not isinstance(data, pd.DataFrame) or len(data) < n_candles:
            # Not enough data or incorrect type, return Hold (0)
            return 0
        
        if 'Open' not in data.columns or 'Close' not in data.columns:
            print("Error: DataFrame must contain 'Open' and 'Close' columns.")
            return 0
        
        # 3. Logic: Check the last N candles
        
        # Get the last N rows of data
        recent_data = data.iloc[-n_candles:]
        
        # A candle is "red" (bearish) if its Close price is less than its Open price.
        # We create a boolean Series where True = Red Candle.
        is_red_series = recent_data['Close'] < recent_data['Open']
        
        # Check if ALL N boolean values are True
        all_are_red = is_red_series.all()
        
        # 4. Generate Signal
        if all_are_red:
            # Condition met: Last N candles were all bearish
            return n_candles_operation  # Signal
        else:
            # Condition not met
            return 0  # Hold Signal
