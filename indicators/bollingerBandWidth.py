import pandas_ta as ta
import pandas as pd
import typing as t
from .indicator import Indicator
from indicators.constants import (
    BB_LENGTH,
    BB_STD,
    BB_VARIATION_MAX,
    BB_VARIATION_MIN,
    CLOSE_COLUMN,
    OPERATION_TYPE,
    SIGNAL_BUY,
    SIGNAL_HOLD
)

class BollingerBandWidth(Indicator):
    """
    Evaluates volatility by measuring the width of the Bollinger Bands.
    Useful for detecting "Squeezes" (low volatility) or "Expansion" (high volatility).
    
    Parameters:
    - 'bb_length': (int) Period for the Bollinger Bands (e.g., 20).
    - 'bb_std': (float) Standard deviation (e.g., 2.0).
    - 'variation_min': (float, optional) Minimum width threshold.
    - 'variation_max': (float, optional) Maximum width threshold.
    - 'operation_type': (int) Signal to return if the condition is met.
    """

    def evaluate(self, data: pd.DataFrame, params: t.Optional[t.Dict[str, t.Any]] = None) -> int:
        if params is None:
            params = self.params

        # --- 1. Parameter Extraction ---
        try:
            length = int(params.get(BB_LENGTH, 20))
            std = float(params.get(BB_STD, 2.0))
            var_min = params.get(BB_VARIATION_MIN, 3.0)
            var_max = params.get(BB_VARIATION_MAX)
            operation_type =int(params.get(OPERATION_TYPE, SIGNAL_BUY))
        except (ValueError, TypeError):
            return SIGNAL_HOLD

        # --- 2. Data Validation ---
        if len(data) < length or CLOSE_COLUMN not in data.columns:
            return SIGNAL_HOLD

        # --- 3. Indicator Calculation ---
        # pandas_ta.bbands provides the 'BBB' column which is the Bandwidth
        bb = ta.bbands(data[CLOSE_COLUMN], length=length, std=std)
        
        if bb is None or bb.empty:
            return SIGNAL_HOLD

        # pandas_ta column naming for bandwidth: BBB_length_std
        # Note: BBB = (Upper - Lower) / Mid * 100
        bandwidth_col = f"BBB_{length}_{std}_{std}"
        current_bandwidth = bb[bandwidth_col].iloc[-1]

        # --- 4. Logic Execution ---
        # Check Min threshold
        if var_min is not None:
            if current_bandwidth < float(var_min):
                return SIGNAL_HOLD

        # Check Max threshold
        if var_max is not None:
            if current_bandwidth > float(var_max):
                return SIGNAL_HOLD

        # If we passed both checks (or if no checks were present), return signal
        return operation_type