import pandas as pd
import typing as t
from .indicator import Indicator
from typing import Optional, Dict, Any
from indicators.constants import ( 
    CLOSE_COLUMN,
    OPEN_COLUMN,
    N_CANDLES_LENGTH,
    N_CANDLES_OPERATION,
    N_CANDLES_OFFSET,
    SIGNAL_HOLD
)

class NGreenCandles(Indicator):
    """
    An indicator that returns 1 (buy) if the most recent N candles
    are all green (bullish), otherwise it returns 0.
    
    A candle is considered green (bullish) if Close > Open.
    """

    def evaluate(self, data: pd.DataFrame, params: Optional[Dict[str, Any]] = None) -> int:
        """
        Evaluates the indicator condition using financial data.

        Args:
            data (pd.DataFrame): DataFrame containing financial data 
                                 (must have 'Open' and 'Close' columns).
            params (Optional[Dict]): Dictionary containing 'n_candles' (int) 
                                     specifying the required number of consecutive green candles.

        Returns:
            1 if the last 'n_candles' are all green, otherwise 0.
        """

        # Use instance parameters if none are provided
        if (params is None):
            params = self.params

        # --- 1. Parameter Validation ---
        if params is None or N_CANDLES_LENGTH not in params:
            raise ValueError("Parameters must be provided and contain the key N_CANDLES_LENGTH.")
        
        if params is None or N_CANDLES_OPERATION not in params:
            raise ValueError("Parameters must be provided and contain the key N_CANDLES_OPERATION.")
        
        N = extractIntParam(params, N_CANDLES_LENGTH)

        n_candles_operation = extractIntParam(params, N_CANDLES_OPERATION)
        if 2 < n_candles_operation <= 0:
            raise ValueError("N_CANDLES_OPERATION must be a 1 or 2.")
            
        Y = extractIntParam(params, N_CANDLES_OFFSET)

        # --- 2. Data Validation ---
        required_cols = [OPEN_COLUMN, CLOSE_COLUMN]
        if not all(col in data.columns for col in required_cols):
            raise ValueError(f"DataFrame must contain the columns: {required_cols}")
            
        if len(data) < N:
            # Not enough historical data to satisfy the N lookback period
            return 0 
        
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
        
        # --- 4. Determine Candle Color ---
        # A candle is green (bullish) if Close > Open.
        # We create a boolean Series where True = Green Candle.
        is_green_series = recent_data[CLOSE_COLUMN] > recent_data[OPEN_COLUMN]
        
        # --- 5. Evaluate Condition ---
        # The condition is met if ALL values in the Series are True.
        is_all_green = is_green_series.all()

        # --- 6. Return Result ---
        return n_candles_operation if is_all_green else SIGNAL_HOLD

def extractIntParam(params: Dict[str, Any], key: str) -> int:
    N_raw = params[key]
    try:
        # Attempt to convert string (or other types) to an integer
        N = int(N_raw)
        
        if N < 0:
            raise ValueError
        
        return N
    except (ValueError, TypeError):
        # This triggers if int() fails or if N <= 0
        raise ValueError(f"{key} must be a string or number representing a positive integer.")