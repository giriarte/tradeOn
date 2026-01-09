import pandas_ta as ta
import pandas as pd
import typing as t
from .indicator import Indicator
from indicators.constants import (
    CLOSE_COLUMN,
    SIGNAL_SELL,
    SIGNAL_HOLD
)

class BelowEMA(Indicator):
    """
    Checks if the current price is strictly below a calculated EMA.
    
    Parameters:
    - 'ema_length': (int) The period for the EMA calculation (e.g., 20, 50, 200).
    - 'operation_type': (int) Signal to return if price < EMA (default SIGNAL_SELL).
    """

    def evaluate(self, data: pd.DataFrame, params: t.Optional[t.Dict[str, t.Any]] = None) -> int:
        if params is None:
            params = self.params

        # --- 1. Parameter Extraction ---
        try:
            ema_length = int(params.get('ema_length', 20))
            operation_type = int(params.get('operation_type', SIGNAL_SELL))
        except (ValueError, TypeError):
            return SIGNAL_HOLD

        # --- 2. Data Validation ---
        if len(data) < ema_length or CLOSE_COLUMN not in data.columns:
            return SIGNAL_HOLD

        # --- 3. Indicator Calculation ---
        ema_series = ta.ema(data[CLOSE_COLUMN], length=ema_length)
        
        if ema_series is None or ema_series.empty:
            return SIGNAL_HOLD

        current_price = data[CLOSE_COLUMN].iloc[-1]
        current_ema = ema_series.iloc[-1]

        # --- 4. Logic Execution ---
        # Trigger if the price is currently below the average
        if current_price < current_ema:
            return operation_type

        return SIGNAL_HOLD