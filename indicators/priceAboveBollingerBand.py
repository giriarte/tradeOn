import pandas_ta as ta
import pandas as pd
import typing as t
from .indicator import Indicator
from indicators.constants import (
    BB_LENGTH,
    BB_STD,
    CLOSE_COLUMN,
    OPERATION_TYPE,
    SIGNAL_SELL,
    SIGNAL_HOLD
)

class PriceAboveBollingerBand(Indicator):
    """
    Checks if the current price is currently above the Upper Bollinger Band.
    
    Parameters:
    - 'bb_length': (int) Period for the Bollinger Bands (e.g., 20).
    - 'bb_std': (float) Standard deviation (e.g., 2.0).
    - 'operation_type': (int) Signal to return if price > upper band (default SIGNAL_SELL).
    """

    def evaluate(self, data: pd.DataFrame, params: t.Optional[t.Dict[str, t.Any]] = None) -> int:
        if params is None:
            params = self.params

        # --- 1. Parameter Extraction ---
        try:
            length = int(params.get(BB_LENGTH, 20))
            std = float(params.get(BB_STD, 2.0))
            operation_type = int(params.get(OPERATION_TYPE, SIGNAL_SELL))
        except (ValueError, TypeError):
            return SIGNAL_HOLD

        # --- 2. Data Validation ---
        if len(data) < length or CLOSE_COLUMN not in data.columns:
            return SIGNAL_HOLD

        # --- 3. Indicator Calculation ---
        bb = ta.bbands(data[CLOSE_COLUMN], length=length, std=std)
        
        if bb is None or bb.empty:
            return SIGNAL_HOLD

        # Standard pandas_ta naming: BBU_length_std
        upper_band_col = f"BBU_{length}_{std}_{std}"
        
        current_price = data[CLOSE_COLUMN].iloc[-1]
        current_upper_band = bb[upper_band_col].iloc[-1]

        # --- 4. Logic Execution ---
        # Trigger if price is currently "piercing" the upper band
        if current_price > current_upper_band:
            return operation_type

        return SIGNAL_HOLD