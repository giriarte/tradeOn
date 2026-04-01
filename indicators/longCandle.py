import pandas as pd
import typing as t
from .indicator import Indicator
from indicators.constants import (
    HIGH_COLUMN,
    LOW_COLUMN,
    SIGNAL_BUY,
    SIGNAL_HOLD
)

class LongCandle(Indicator):
    """
    Checks if the length of the current candle is larger than the average 
    size of the previous N candles by a specific multiplier.
    
    Parameters:
    - 'lookback': (int) Number of previous candles to average (default 20).
    - 'multiplier': (float) How much larger the candle must be (e.g., 2.0 for 2x avg).
    - 'operation_type': (int) Signal to return if condition is met (default SIGNAL_BUY).
    """

    def evaluate(self, data: pd.DataFrame, params: t.Optional[t.Dict[str, t.Any]] = None) -> int:
        if params is None:
            params = self.params

        # --- 1. Parameter Extraction ---
        try:
            lookback = int(params.get('lookback', 30))
            multiplier = float(params.get('multiplier', 1.5))
            operation_type = params.get('operation_type', SIGNAL_BUY)
        except (ValueError, TypeError):
            return SIGNAL_HOLD

        # --- 2. Data Validation ---
        if len(data) < (lookback + 1) or HIGH_COLUMN not in data.columns or LOW_COLUMN not in data.columns:
            return SIGNAL_HOLD

        # --- 3. Logic Execution ---
        # Calculate the absolute length for all candles
        # Length = |High - Low|
        lengths = (data[HIGH_COLUMN] - data[LOW_COLUMN]).abs()

        # Get historical average length excluding the current candle
        historical_lengths = lengths.iloc[-(lookback + 1):-1]
        avg_length = historical_lengths.mean()
        if avg_length <= 0:
            return SIGNAL_HOLD

        current_length = lengths.iloc[-1]
        # Check if the current candle is "Long" enough
        if current_length >= (avg_length * multiplier):
            return operation_type

        return SIGNAL_HOLD