import pandas_ta as ta
import pandas as pd
import typing as t
from .indicator import Indicator
from indicators.constants import (
    ADX_LENGTH,
    CLOSE_COLUMN,
    DMP_MAX,
    DMP_MIN,
    HIGH_COLUMN,
    LOW_COLUMN,
    OPERATION_TYPE,
    SIGNAL_BUY,
    SIGNAL_HOLD
)

class DMPRange(Indicator):
    """
    Evaluates if the Positive Directional Indicator (+DI / DMP) 
    falls within a specific range.
    
    Parameters:
    - 'adx_length': (int) Period for the calculation (default 14).
    - 'dmp_min': (float, optional) Minimum +DI value required.
    - 'dmp_max': (float, optional) Maximum +DI value allowed.
    - 'operation_type': (int) Signal to return if conditions are met.
    """

    def evaluate(self, data: pd.DataFrame, params: t.Optional[t.Dict[str, t.Any]] = None) -> int:
        if params is None:
            params = self.params

        # --- 1. Parameter Extraction ---
        try:
            length = int(params.get(ADX_LENGTH, 14))
            dmp_min = params.get(DMP_MIN)
            dmp_max = params.get(DMP_MAX)
            operation_type = params.get(OPERATION_TYPE, SIGNAL_BUY)
        except (ValueError, TypeError):
            print("Invalid parameters provided to DMPRange indicator.")
            return SIGNAL_HOLD

        # --- 2. Data Validation ---
        if len(data) < (length * 2) or HIGH_COLUMN not in data.columns:
            return SIGNAL_HOLD

        # --- 3. Indicator Calculation ---
        # pandas_ta.adx returns a DataFrame containing:
        # [ADX_length, DMP_length, DMN_length]
        adx_df = ta.adx(data[HIGH_COLUMN], data[LOW_COLUMN], data[CLOSE_COLUMN], length=length)
        
        if adx_df is None or adx_df.empty:
            return SIGNAL_HOLD

        dmp_col = f"DMP_{length}"
        current_dmp = adx_df[dmp_col].iloc[-1]

        if dmp_min is None and dmp_max is None:
            print("DMPRange: No min or max bounds set; defaulting to SIGNAL_HOLD.")
            return SIGNAL_HOLD
        
        # --- 4. Range Logic ---
        # Check Minimum Bullish Pressure
        if dmp_min is not None:
            if current_dmp < float(dmp_min):
                return SIGNAL_HOLD

        # Check Maximum Bullish Pressure (Overextension check)
        if dmp_max is not None:
            if current_dmp > float(dmp_max):
                return SIGNAL_HOLD

        print(f"DMPRange: DMP {current_dmp} within range; returning signal.")
        return operation_type