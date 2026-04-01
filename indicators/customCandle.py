import pandas as pd
import typing as t
from .indicator import Indicator
from indicators.constants import (
    OPEN_COLUMN,
    CLOSE_COLUMN,
    HIGH_COLUMN,
    LOW_COLUMN,
    SIGNAL_BUY,
    SIGNAL_HOLD
)

class CustomCandle(Indicator):
    """
    Evaluates a candle based on the percentage of the total range occupied by its wicks.
    
    Parameters:
    - 'upper_wick_min': (float) Min % of candle range for upper wick (0-100).
    - 'upper_wick_max': (float) Max % of candle range for upper wick (0-100).
    - 'lower_wick_min': (float) Min % of candle range for lower wick (0-100).
    - 'lower_wick_max': (float) Max % of candle range for lower wick (0-100).
    - 'operation_type': (int) Signal to return if conditions met (default SIGNAL_BUY).
    """

    def evaluate(self, data: pd.DataFrame, params: t.Optional[t.Dict[str, t.Any]] = None) -> int:
        if params is None:
            params = self.params

        # --- 1. Parameter Extraction ---
        try:
            uw_min = float(params.get('upper_wick_min', 0))
            uw_max = float(params.get('upper_wick_max', 100))
            lw_min = float(params.get('lower_wick_min', 0))
            lw_max = float(params.get('lower_wick_max', 100))
            operation_type = params.get('operation_type', SIGNAL_BUY)
        except (ValueError, TypeError):
            return SIGNAL_HOLD

        # --- 2. Data Validation ---
        if data.empty or HIGH_COLUMN not in data.columns:
            return SIGNAL_HOLD

        # --- 3. Logic Execution ---
        last_row = data.iloc[-1]
        high = last_row[HIGH_COLUMN]
        low = last_row[LOW_COLUMN]
        open_p = last_row[OPEN_COLUMN]
        close_p = last_row[CLOSE_COLUMN]

        total_range = high - low

        # Handle flat candles (avoid division by zero)
        if total_range == 0:
            return SIGNAL_HOLD

        # Calculate Wick Sizes
        # Upper wick is distance from high to the top of the body (max of open/close)
        upper_wick_size = high - max(open_p, close_p)
        # Lower wick is distance from the bottom of the body (min of open/close) to low
        lower_wick_size = min(open_p, close_p) - low

        # Convert to Percentages relative to total candle size
        uw_pct = (upper_wick_size / total_range) * 100
        lw_pct = (lower_wick_size / total_range) * 100

        # --- 4. Boundary Checks ---
        if not (uw_min <= uw_pct <= uw_max):
            return SIGNAL_HOLD
            
        if not (lw_min <= lw_pct <= lw_max):
            return SIGNAL_HOLD

        return operation_type