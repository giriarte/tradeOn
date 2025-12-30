import pandas as pd
import typing as t
from .indicator import Indicator
from indicators.constants import (
    CLOSE_COLUMN,
    LOW_COLUMN,
    OPERATION_TYPE,
    SIGNAL_BUY,
    SIGNAL_HOLD,
    SUPPORT_LOOKBACK,
    TOLERANCE_PCT
)

class NearSupport(Indicator):
    """
    Identifies a dynamic support level (lowest price in lookback) and 
    checks if current price is within a tolerance range of that level.
    
    Parameters:
    - 'support_lookback': (int) Number of candles to look back to find the low.
    - 'tolerance_pct': (float) The allowed distance percentage (e.g., 0.5 for 0.5%).
    - 'operation_type': (int) Signal to return if within range (default SIGNAL_BUY).
    """

    def evaluate(self, data: pd.DataFrame, params: t.Optional[t.Dict[str, t.Any]] = None) -> int:
        if params is None:
            params = self.params

        # --- 1. Parameter Extraction ---
        try:
            lookback = int(params.get(SUPPORT_LOOKBACK, 20))
            tolerance_pct = float(params.get(TOLERANCE_PCT, 0.5))
            operation_type = int(params.get(OPERATION_TYPE, SIGNAL_BUY))
        except (ValueError, TypeError):
            print("Invalid parameter types for NearSupport indicator.")
            return SIGNAL_HOLD

        # --- 2. Data Validation ---
        # We need at least lookback + 1 (for current candle)
        if len(data) < (lookback + 1) or LOW_COLUMN not in data.columns:
            return SIGNAL_HOLD

        # --- 3. Identify Support Level ---
        # We look at the 'Low' of the last N candles, excluding the current one
        # Current index is -1, so lookback window is from -(lookback+1) to -2
        historical_data = data[LOW_COLUMN].iloc[-(lookback + 1):-1]
        support_level = historical_data.min()

        # --- 4. Logic Execution ---
        current_price = data[CLOSE_COLUMN].iloc[-1]
        
        # Calculate percentage difference from the dynamic support
        # We use absolute difference so it works whether price is slightly above or below
        diff_pct = (abs(current_price - support_level) / support_level) * 100

        if diff_pct <= tolerance_pct:
            print(f'close value found in NearSupport indicator for level ${support_level} with tolerance {tolerance_pct}%')
            return operation_type

        return SIGNAL_HOLD