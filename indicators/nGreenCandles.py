import pandas as pd
import typing as t
from .indicator import Indicator
from typing import Optional, Dict, Any

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
        
        # --- 1. Parameter Validation ---
        if params is None or 'n_candles' not in params:
            raise ValueError("Parameters must be provided and contain the key 'n_candles'.")
        
        if params is None or 'n_candles_operation' not in params:
            raise ValueError("Parameters must be provided and contain the key 'n_candles_operation'.")
            
        N = params['n_candles']
        if not isinstance(N, int) or N <= 0:
            raise ValueError("'n_candles' must be a positive integer.")
        
        n_candles_operation = params['n_candles_operation']
        if not isinstance(N, int) or 2 < N <= 0:
            raise ValueError("'n_candles_operation' must be a 1 or 2.")
            
        # --- 2. Data Validation ---
        required_cols = ['Open', 'Close']
        if not all(col in data.columns for col in required_cols):
            raise ValueError(f"DataFrame must contain the columns: {required_cols}")
            
        if len(data) < N:
            # Not enough historical data to satisfy the N lookback period
            return 0 
        
        # --- 3. Extract Recent Data ---
        # Get the last N rows of the DataFrame
        recent_data = data.iloc[-N:]
        
        # --- 4. Determine Candle Color ---
        # A candle is green (bullish) if Close > Open.
        # We create a boolean Series where True = Green Candle.
        is_green_series = recent_data['Close'] > recent_data['Open']
        
        # --- 5. Evaluate Condition ---
        # The condition is met if ALL values in the Series are True.
        is_all_green = is_green_series.all()
        
        # --- 6. Return Result ---
        # Convert the boolean result (True/False) to the required integer (1/2).
        return n_candles_operation if is_all_green else 0
