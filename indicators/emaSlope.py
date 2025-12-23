import pandas_ta as ta
import pandas as pd
import typing as t
from .indicator import Indicator
from indicators.constants import (
    CLOSE_COLUMN,
    EMA_LENGTH,
    LOOKBACK,
    MIN_SLOPE_PCT,
    OPERATION_TYPE,
    SIGNAL_BUY,
    SIGNAL_HOLD
)

class EMASlope(Indicator):
    """
    Measures the trend intensity by calculating the percentage slope of an EMA.
    This version uses the absolute value (modulus) of the slope.
    
    Parameters:
    - 'ema_length': (int) Period for the EMA calculation.
    - 'lookback': (int) Number of bars back to compare.
    - 'min_slope_pct': (float) The minimum percentage change required (e.g., 0.05 for 0.05%).
    - 'operation_type': (int) The signal to return if the slope exceeds the threshold.
    """

    def evaluate(self, data: pd.DataFrame, params: t.Optional[t.Dict[str, t.Any]] = None) -> int:
        if params is None:
            params = self.params

        # --- 1. Parameter Extraction ---
        try:
            ema_length = int(params.get(EMA_LENGTH, 20))
            lookback = int(params.get(LOOKBACK, 5))
            min_slope_pct = float(params.get(MIN_SLOPE_PCT, 1.0))
            # Default to SIGNAL_BUY as a "Trend Active" confirmation
            operation_type = params.get(OPERATION_TYPE, SIGNAL_BUY)
        except (ValueError, TypeError):
            return SIGNAL_HOLD

        # --- 2. Data Validation ---
        if len(data) < (ema_length + lookback) or CLOSE_COLUMN not in data.columns:
            return SIGNAL_HOLD

        # --- 3. Indicator Calculation ---
        ema_series = ta.ema(data[CLOSE_COLUMN], length=ema_length)
        
        if ema_series is None or len(ema_series) < lookback + 1:
            return SIGNAL_HOLD

        current_ema = ema_series.iloc[-1]
        previous_ema = ema_series.iloc[-(lookback + 1)]

        if previous_ema == 0:  # Avoid division by zero
            return SIGNAL_HOLD

        # --- 4. Percentage Slope with Modulus ---
        # Formula: abs((Current - Previous) / Previous) * 100
        raw_slope_pct = ((current_ema - previous_ema) / previous_ema) * 100
        abs_slope_pct = abs(raw_slope_pct)

        # --- 5. Threshold Logic ---
        # If the absolute percentage change is greater than our "cap" or threshold,
        # we consider the trend strong enough to trade.
        if abs_slope_pct >= min_slope_pct:
            return operation_type

        return SIGNAL_HOLD