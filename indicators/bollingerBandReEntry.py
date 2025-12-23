import pandas_ta as ta
import pandas as pd
import typing as t
from .indicator import Indicator
from indicators.constants import (
    BB_LENGTH,
    BB_STD,
    CLOSE_COLUMN,
    OPERATION_TYPE,
    SIGNAL_BUY,
    SIGNAL_SELL,
    SIGNAL_HOLD
)

class BollingerBandReEntry(Indicator):
    """
    Detects when price re-enters the Bollinger Bands from the outside.
    
    Parameters:
    - 'bb_length': (int) Period for the Bollinger Bands (e.g., 20).
    - 'bb_std': (float) Standard deviation (e.g., 2.0).
    - 'operation_type': (int) SIGNAL_BUY (Re-entry from below) 
                             SIGNAL_SELL (Re-entry from above).
    """

    def evaluate(self, data: pd.DataFrame, params: t.Optional[t.Dict[str, t.Any]] = None) -> int:
        if params is None:
            params = self.params

        # --- 1. Parameter Extraction ---
        try:
            length = int(params.get(BB_LENGTH, 20))
            std = float(params.get(BB_STD, 2.0))
            operation_type = int(params.get(OPERATION_TYPE, SIGNAL_BUY))
        except (ValueError, TypeError):
            return SIGNAL_HOLD

        # --- 2. Data Validation ---
        if len(data) < (length + 1) or CLOSE_COLUMN not in data.columns:
            return SIGNAL_HOLD

        # --- 3. Indicator Calculation ---
        # pandas_ta returns a DataFrame with columns: BBL_length_std, BBM_length_std, BBU_length_std
        bb = ta.bbands(data[CLOSE_COLUMN], length=length, std=std)
        
        if bb is None or bb.empty:
            return SIGNAL_HOLD

        # Identify column names dynamically
        lower_col = f"BBL_{length}_{std}_{std}"
        upper_col = f"BBU_{length}_{std}_{std}"

        # Get Current and Previous values
        curr_price = data[CLOSE_COLUMN].iloc[-1]
        prev_price = data[CLOSE_COLUMN].iloc[-2]
        
        curr_lower = bb[lower_col].iloc[-1]
        prev_lower = bb[lower_col].iloc[-2]
        
        curr_upper = bb[upper_col].iloc[-1]
        prev_upper = bb[upper_col].iloc[-2]

        # --- 4. Re-Entry Logic ---
        if operation_type == SIGNAL_BUY:
            # Bullish Re-entry: Prev price was BELOW lower band, Curr price is ABOVE lower band
            # We also ensure it hasn't already pierced the upper band in one go
            if prev_price < prev_lower and curr_price > curr_lower:
                return SIGNAL_BUY
                
        elif operation_type == SIGNAL_SELL:
            # Bearish Re-entry: Prev price was ABOVE upper band, Curr price is BELOW upper band
            if prev_price > prev_upper and curr_price < curr_upper:
                return SIGNAL_SELL

        return SIGNAL_HOLD