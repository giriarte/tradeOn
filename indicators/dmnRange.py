import pandas_ta as ta
import pandas as pd
import typing as t
from .indicator import Indicator
from indicators.constants import (
    ADX_LENGTH,
    CLOSE_COLUMN,
    DMN_MAX,
    DMN_MIN,
    HIGH_COLUMN,
    LOW_COLUMN,
    OPERATION_TYPE,
    SIGNAL_SELL,
    SIGNAL_HOLD
)

class DMNRange(Indicator):
    """
    Evaluates if the Negative Directional Indicator (-DI / DMN) 
    falls within a specific range.
    
    Parameters:
    - 'adx_length': (int) Period for the calculation (default 14).
    - 'dmn_min': (float, optional) Minimum -DI value required.
    - 'dmn_max': (float, optional) Maximum -DI value allowed.
    - 'operation_type': (int) Signal to return if conditions are met (default SIGNAL_SELL).
    """

    def evaluate(self, data: pd.DataFrame, params: t.Optional[t.Dict[str, t.Any]] = None) -> int:
        if params is None:
            params = self.params

        # --- 1. Parameter Extraction ---
        try:
            length = int(params.get(ADX_LENGTH, 14))
            dmn_min = params.get(DMN_MIN)
            dmn_max = params.get(DMN_MAX)
            operation_type = params.get(OPERATION_TYPE, SIGNAL_SELL)
        except (ValueError, TypeError):
            print("Invalid parameters provided to DMNRange indicator.")
            return SIGNAL_HOLD

        # --- 2. Data Validation ---
        if len(data) < (length * 2) or HIGH_COLUMN not in data.columns:
            return SIGNAL_HOLD

        # --- 3. Indicator Calculation ---
        # pandas_ta.adx returns a DataFrame containing [ADX_len, DMP_len, DMN_len]
        adx_df = ta.adx(data[HIGH_COLUMN], data[LOW_COLUMN], data[CLOSE_COLUMN], length=length)
        
        if adx_df is None or adx_df.empty:
            return SIGNAL_HOLD

        dmn_col = f"DMN_{length}"
        current_dmn = adx_df[dmn_col].iloc[-1]

        if dmn_min is None and dmn_max is None:
            print("DMNRange: No min or max bounds set; defaulting to SIGNAL_HOLD.")
            return SIGNAL_HOLD
        
        # --- 4. Range Logic ---
        # Check Minimum Bearish Pressure
        if dmn_min is not None:
            if current_dmn < float(dmn_min):
                return SIGNAL_HOLD

        # Check Maximum Bearish Pressure
        if dmn_max is not None:
            if current_dmn > float(dmn_max):
                return SIGNAL_HOLD

        print(f"DMNRange: DMN {current_dmn} within range; returning signal.")
        return operation_type