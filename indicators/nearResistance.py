import pandas as pd
import typing as t
from .indicator import Indicator
from indicators.constants import (
    CLOSE_COLUMN,
    HIGH_COLUMN,
    SIGNAL_SELL,
    SIGNAL_HOLD
)

class NearResistance(Indicator):
    """
    Identifies a dynamic resistance level (highest price in lookback) and 
    checks if the current price is within a tolerance range of that level.
    
    Parameters:
    - 'resistance_lookback': (int) Number of candles to look back to find the high.
    - 'tolerance_pct': (float) The allowed distance percentage (e.g., 0.5 for 0.5%).
    - 'operation_type': (int) Signal to return if within range (default SIGNAL_SELL).
    """

    def evaluate(self, data: pd.DataFrame, params: t.Optional[t.Dict[str, t.Any]] = None) -> int:
        if params is None:
            params = self.params

        # --- 1. Parameter Extraction ---
        try:
            lookback = int(params.get('resistance_lookback', 20))
            tolerance_pct = float(params.get('tolerance_pct', 0.5))
            operation_type = params.get('operation_type', SIGNAL_SELL)
        except (ValueError, TypeError):
            return SIGNAL_HOLD

        # --- 2. Data Validation ---
        # Need lookback + 1 to include the current candle comparison
        if len(data) < (lookback + 1) or HIGH_COLUMN not in data.columns:
            return SIGNAL_HOLD

        # --- 3. Identify Resistance Level ---
        # Scan the 'High' of historical candles, excluding the current one (-1)
        historical_highs = data[HIGH_COLUMN].iloc[-(lookback + 1):-1]
        resistance_level = historical_highs.max()

        # --- 4. Logic Execution ---
        current_price = data[CLOSE_COLUMN].iloc[-1]
        
        # Calculate percentage difference from the dynamic resistance
        # Formula: (abs(Price - Resistance) / Resistance) * 100
        diff_pct = (abs(current_price - resistance_level) / resistance_level) * 100

        if diff_pct <= tolerance_pct:
            return operation_type

        return SIGNAL_HOLD