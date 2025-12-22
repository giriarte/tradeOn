import typing as t
import pandas as pd
from .indicator import Indicator
from indicators.constants import ( 
    CLOSE_COLUMN,
    OPEN_COLUMN,
    N_CANDLES_LENGTH,
    N_CANDLES_OPERATION,
    N_CANDLES_OFFSET,
    SIGNAL_HOLD
)

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
        
        # Use instance parameters if none are provided
        if (params is None):
            params = self.params

        # 1. Parameter Handling (N)
        default_n = 3 # Default lookback if not provided

        n_candles_operation = 1 # Default operation is to buy, but it can be changed by parameter to 2 (sell)
        N = default_n
        
        if params and N_CANDLES_LENGTH in params:
            N = params[N_CANDLES_LENGTH]
            
        if params and N_CANDLES_OPERATION in params:
            n_candles_operation = params[N_CANDLES_OPERATION]
        
        Y = params.get(N_CANDLES_OFFSET, 0)  # Offset (e.g., 0 for current, 2 for two periods ago)

        # 2. Data Validation
        if not isinstance(data, pd.DataFrame) or len(data) < N:
            # Not enough data or incorrect type, return Hold (0)
            return 0
        
        if OPEN_COLUMN not in data.columns or CLOSE_COLUMN not in data.columns:
            print("Error: DataFrame must contain 'Open' and 'Close' columns.")
            return 0
        
        # 3. Logic: Check the last N candles
        
        # The end point of the slice (exclusive index)
        # If Y=0, end_index is data_length (last row index + 1) -> data.iloc[start:data_length]
        # If Y=2, end_index is data_length - 2
        end_index = len(data) - Y
        
        # The start point of the slice (inclusive index)
        # Start N periods before the end_index
        start_index = end_index - N

        # --- 3. Extract Recent Data ---
        # Get the last N rows of the DataFrame
        recent_data = data.iloc[start_index:end_index]
        
        # A candle is "red" (bearish) if its Close price is less than its Open price.
        # We create a boolean Series where True = Red Candle.
        is_red_series = recent_data[CLOSE_COLUMN] < recent_data[OPEN_COLUMN]
        
        # Check if ALL N boolean values are True
        all_are_red = is_red_series.all()
        
        # 4. Generate Signal
        if all_are_red:
            # Condition met: Last N candles were all bearish
            return n_candles_operation  # Signal
        else:
            # Condition not met
            return SIGNAL_HOLD
