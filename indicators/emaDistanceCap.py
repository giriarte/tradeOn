import pandas_ta as ta
import pandas as pd
import typing as t
from .indicator import Indicator
from indicators.constants import (
    CLOSE_COLUMN,
    DISTANCE_PCT_CAP,
    EMA_LENGTH,
    OPERATION_TYPE,
    SIGNAL_BUY,
    SIGNAL_SELL,
    SIGNAL_HOLD
)

class EMADistanceCap(Indicator):
    """
    Check if the price is above/below an EMA, but ONLY if the distance
    is LESS THAN OR EQUAL to a predefined percentage cap.
    
    Parameters:
    - 'ema_length': (int) Period for the EMA.
    - 'distance_pct_cap': (float) The maximum allowed distance (e.g., 1.5 for 1.5%).
    - 'operation_type': (int) SIGNAL_BUY (Above EMA) or SIGNAL_SELL (Below EMA).
    """

    def evaluate(self, data: pd.DataFrame, params: t.Optional[t.Dict[str, t.Any]] = None) -> int:
        if params is None:
            params = self.params

        # --- 1. Parameter Extraction ---
        ema_length = int(params.get(EMA_LENGTH, 20))
        distance_pct_cap = float(params.get(DISTANCE_PCT_CAP, 1.0))
        operation_type = int(params.get(OPERATION_TYPE, SIGNAL_BUY))

        # --- 2. Data Validation ---
        if len(data) < ema_length or CLOSE_COLUMN not in data.columns:
            return SIGNAL_HOLD

        # --- 3. Indicator Calculation ---
        ema_series = ta.ema(data[CLOSE_COLUMN], length=ema_length)
        
        if ema_series is None or ema_series.empty:
            return SIGNAL_HOLD

        current_price = data[CLOSE_COLUMN].iloc[-1]
        current_ema = ema_series.iloc[-1]

        # Calculate percentage distance from EMA
        # Positive = Above EMA, Negative = Below EMA
        actual_dist_pct = ((current_price - current_ema) / current_ema) * 100

        # --- 4. Logic Execution with CAP ---
        if operation_type == SIGNAL_BUY:
            # Condition: Price must be ABOVE EMA, but within the CAP
            # Example: distance is 0.5% and cap is 1.0% -> TRUE
            # Example: distance is 1.5% and cap is 1.0% -> FALSE (Too far)
            if 0 <= actual_dist_pct <= distance_pct_cap:
                print(f'emaDistanceCap identified for actual percentage ${actual_dist_pct} lower than CAP ${distance_pct_cap}')
                return SIGNAL_BUY
        
        elif operation_type == SIGNAL_SELL:
            # Condition: Price must be BELOW EMA, but within the CAP
            # actual_dist_pct will be negative (e.g., -0.5%)
            if -distance_pct_cap <= actual_dist_pct <= 0:
                print(f'emaDistanceCap identified for actual percentage ${actual_dist_pct} greater than CAP ${distance_pct_cap}')
                return SIGNAL_SELL

        return SIGNAL_HOLD