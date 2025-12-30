import pandas_ta as ta
import pandas as pd
import typing as t
from .indicator import Indicator
from indicators.constants import (
    ADX_LENGTH,
    ADX_MAX,
    ADX_MIN,
    CLOSE_COLUMN,
    HIGH_COLUMN,
    LOW_COLUMN,
    OPERATION_TYPE,
    SIGNAL_BUY,
    SIGNAL_HOLD
)

class ADXRange(Indicator):
    """
    Evaluates if the trend strength (ADX) falls within a specific range.
    
    Parameters:
    - 'adx_length': (int) Period for ADX calculation (default 14).
    - 'adx_min': (float, optional) Minimum ADX value required to signal.
    - 'adx_max': (float, optional) Maximum ADX value allowed to signal.
    - 'operation_type': (int) Signal to return if conditions are met.
    """

    def evaluate(self, data: pd.DataFrame, params: t.Optional[t.Dict[str, t.Any]] = None) -> int:
        if params is None:
            params = self.params

        # --- 1. Parameter Extraction ---
        try:
            length = int(params.get(ADX_LENGTH, 14))
            adx_min = params.get(ADX_MIN)
            adx_max = params.get(ADX_MAX)
            operation_type = int(params.get(OPERATION_TYPE, SIGNAL_BUY))
        except (ValueError, TypeError):
            print("Invalid parameters provided to ADXRange indicator.")
            return SIGNAL_HOLD

        # --- 2. Data Validation ---
        # ADX typically needs 2 * length + 1 samples to stabilize
        if len(data) < (length * 2) or HIGH_COLUMN not in data.columns:
            return SIGNAL_HOLD

        # --- 3. Indicator Calculation ---
        # pandas_ta.adx returns a DataFrame with ADX_14, DMP_14, DMN_14
        adx_df = ta.adx(data[HIGH_COLUMN], data[LOW_COLUMN], data[CLOSE_COLUMN], length=length)
        
        if adx_df is None or adx_df.empty:
            return SIGNAL_HOLD

        adx_col = f"ADX_{length}"
        current_adx = adx_df[adx_col].iloc[-1]

        if adx_min is None and adx_max is None:
            print("ADXRange: No min or max bounds set; defaulting to SIGNAL_HOLD.")
            return SIGNAL_HOLD

        # --- 4. Range Logic ---
        # Check Minimum (Trend must be at least this strong)
        if adx_min is not None:
            if current_adx < float(adx_min):
                return SIGNAL_HOLD

        # Check Maximum (Trend must not exceed this strength)
        if adx_max is not None:
            if current_adx > float(adx_max):
                return SIGNAL_HOLD

        # If it passes both (or no bounds were set), return signal
        print( f"ADXRange: Current ADX={current_adx} within range.")
        return operation_type