import pandas_ta as ta
import pandas as pd
import typing as t
from .indicator import Indicator
from indicators.constants import (
    CLOSE_COLUMN,
    EMA_LENGTH,
    OPERATION_TYPE,
    SIGNAL_BUY,
    SIGNAL_HOLD,
    TOLERANCE_PCT
)

class NearEMA(Indicator):
    """
    Checks if the current price is within a specific percentage distance 
    of a calculated EMA.
    
    Parameters:
    - 'ema_length': (int) The period for the EMA calculation (e.g., 20, 50, 200).
    - 'tolerance_pct': (float) The allowed distance percentage (e.g., 0.3 for 0.3%).
    - 'operation_type': (int) Signal to return if within range (default SIGNAL_BUY).
    """

    def evaluate(self, data: pd.DataFrame, params: t.Optional[t.Dict[str, t.Any]] = None) -> int:
        if params is None:
            params = self.params

        # --- 1. Parameter Extraction ---
        try:
            ema_length = int(params.get(EMA_LENGTH, 20))
            tolerance_pct = float(params.get(TOLERANCE_PCT, 0.5))
            operation_type = params.get(OPERATION_TYPE, SIGNAL_BUY)
        except (ValueError, TypeError):
            print("Invalid parameters for NearEMA indicator.")
            return SIGNAL_HOLD

        # --- 2. Data Validation ---
        if len(data) < ema_length or CLOSE_COLUMN not in data.columns:
            return SIGNAL_HOLD

        # --- 3. Calculate EMA ---
        ema_series = ta.ema(data[CLOSE_COLUMN], length=ema_length)
        
        if ema_series is None or ema_series.empty:
            return SIGNAL_HOLD

        current_price = data[CLOSE_COLUMN].iloc[-1]
        current_ema = ema_series.iloc[-1]

        # --- 4. Proximity Logic ---
        # Calculate absolute percentage difference from the EMA
        # Formula: abs(Price - EMA) / EMA * 100
        diff_pct = (abs(current_price - current_ema) / current_ema) * 100

        if diff_pct <= tolerance_pct:
            print(f"Price is within the {tolerance_pct}% tolerance of the EMA. Operation: {operation_type} is triggered for near EMA indicator.")
            return operation_type

        return SIGNAL_HOLD