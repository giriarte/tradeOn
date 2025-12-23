import pandas_ta as ta
import pandas as pd
import typing as t
from .indicator import Indicator
from indicators.constants import (
    CLOSE_COLUMN,
    EMA_HIGH,
    EMA_LOW,
    OPERATION_TYPE,
    SIGNAL_BUY,
    SIGNAL_SELL,
    SIGNAL_HOLD
)

class EMACross(Indicator):
    """
    Detects a crossover between two EMAs (Fast and Slow).
    
    Parameters:
    - 'ema_low': (int) Period for the fast EMA (e.g., 9 or 50).
    - 'ema_high': (int) Period for the slow EMA (e.g., 21 or 200).
    - 'operation_type': (int) SIGNAL_BUY (checks for Fast crossing ABOVE Slow)
                             SIGNAL_SELL (checks for Fast crossing BELOW Slow).
    """

    def evaluate(self, data: pd.DataFrame, params: t.Optional[t.Dict[str, t.Any]] = None) -> int:
        if params is None:
            params = self.params

        # --- 1. Parameter Extraction ---
        try:
            low_period = int(params.get(EMA_LOW, 9))
            high_period = int(params.get(EMA_HIGH, 21))
            operation_type = int(params.get(OPERATION_TYPE, SIGNAL_BUY))
        except (ValueError, TypeError):
            return SIGNAL_HOLD

        # --- 2. Data Validation ---
        # We need at least the high_period + 1 bars to compare current vs previous state
        if len(data) < (high_period + 1) or CLOSE_COLUMN not in data.columns:
            return SIGNAL_HOLD

        # --- 3. Indicator Calculation ---
        ema_low_series = ta.ema(data[CLOSE_COLUMN], length=low_period)
        ema_high_series = ta.ema(data[CLOSE_COLUMN], length=high_period)
        
        if ema_low_series is None or ema_high_series is None:
            return SIGNAL_HOLD

        # Get values for the current bar (index -1)
        curr_low = ema_low_series.iloc[-1]
        curr_high = ema_high_series.iloc[-1]
        
        # Get values for the previous bar (index -2)
        prev_low = ema_low_series.iloc[-2]
        prev_high = ema_high_series.iloc[-2]

        # --- 4. Crossover Logic ---
        if operation_type == SIGNAL_BUY:
            # Bullish Cross: Low EMA was below High, and is now above High
            if prev_low <= prev_high and curr_low > curr_high:
                return SIGNAL_BUY
                
        elif operation_type == SIGNAL_SELL:
            # Bearish Cross: Low EMA was above High, and is now below High
            if prev_low >= prev_high and curr_low < curr_high:
                return SIGNAL_SELL

        return SIGNAL_HOLD