import pandas as pd
import typing as t
from .indicator import Indicator
from indicators.constants import (
    OPEN_COLUMN,
    CLOSE_COLUMN,
    SIGNAL_BUY,
    SIGNAL_HOLD
)

class LongBodyCandle(Indicator):
    """
    Checks if the body of the current candle is larger than the average body 
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
            lookback = int(params.get('lookback', 20))
            multiplier = float(params.get('multiplier', 2.0))
            operation_type = params.get('operation_type', SIGNAL_BUY)
        except (ValueError, TypeError):
            return SIGNAL_HOLD

        # --- 2. Data Validation ---
        if len(data) < (lookback + 1) or CLOSE_COLUMN not in data.columns or OPEN_COLUMN not in data.columns:
            return SIGNAL_HOLD

        # --- 3. Logic Execution ---
        # Calculate the absolute body size for all candles
        # Body Size = |Close - Open|
        body_sizes = (data[CLOSE_COLUMN] - data[OPEN_COLUMN]).abs()

        # Get historical average body size excluding the current candle
        historical_bodies = body_sizes.iloc[-(lookback + 1):-1]
        avg_body_size = historical_bodies.mean()

        if avg_body_size <= 0:
            return SIGNAL_HOLD

        current_body_size = body_sizes.iloc[-1]

        # Check if the current candle is "Long" enough
        if current_body_size >= (avg_body_size * multiplier):
            return operation_type

        return SIGNAL_HOLD