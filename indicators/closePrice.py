import pandas as pd
import typing as t
from .indicator import Indicator
from indicators.constants import (
    CLOSE_COLUMN,
    SIGNAL_BUY,
    SIGNAL_HOLD
)

class ClosePrice(Indicator):
    """
    Checks if the current price is within a specific percentage distance 
    of a defined price level
    
    Parameters:
    - 'target_level': (float) The price value.
    - 'tolerance_pct': (float) The allowed distance percentage (e.g., 0.5 for 0.5%).
    - 'operation_type': (int) Signal to return if within range.
    """

    def evaluate(self, data: pd.DataFrame, params: t.Optional[t.Dict[str, t.Any]] = None) -> int:
        if params is None:
            params = self.params

        # --- 1. Parameter Extraction ---
        try:
            target_level = float(params.get('target_level'))
            tolerance_pct = float(params.get('tolerance_pct', 0.5))
            operation_type = params.get('operation_type', SIGNAL_BUY)
        except (ValueError, TypeError, KeyError):
            print("Error: Invalid parameters for ClosePrice indicator.")
            # If target_level is missing or invalid, we cannot evaluate
            return SIGNAL_HOLD

        # --- 2. Data Validation ---
        if data.empty or CLOSE_COLUMN not in data.columns:
            return SIGNAL_HOLD

        # --- 3. Logic Execution ---
        current_price = data[CLOSE_COLUMN].iloc[-1]
        
        # Calculate the absolute percentage difference
        # Formula: abs(Price - Level) / Level * 100
        diff_pct = abs(current_price - target_level) / target_level * 100

        # Check if the price is "close enough"
        if diff_pct <= tolerance_pct:
            return operation_type

        return SIGNAL_HOLD