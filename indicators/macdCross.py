import pandas_ta as ta
import pandas as pd
import typing as t
from .indicator import Indicator
from indicators.constants import (
    CLOSE_COLUMN,
    MACD_FAST,
    MACD_SIGNAL,
    MACD_SLOW,
    OPERATION_TYPE,
    SIGNAL_BUY,
    SIGNAL_SELL,
    SIGNAL_HOLD
)

class MACDCross(Indicator):
    """
    Detects a crossover between the MACD line and the Signal line.
    
    Parameters:
    - 'macd_fast': (int) The short-period EMA (default 12).
    - 'macd_slow': (int) The long-period EMA (default 26).
    - 'macd_signal': (int) The signal line EMA (default 9).
    - 'operation_type': (int) SIGNAL_BUY (MACD crosses ABOVE Signal)
                             SIGNAL_SELL (MACD crosses BELOW Signal).
    """

    def evaluate(self, data: pd.DataFrame, params: t.Optional[t.Dict[str, t.Any]] = None) -> int:
        if params is None:
            params = self.params

        # --- 1. Parameter Extraction ---
        try:
            fast = int(params.get(MACD_FAST, 12))
            slow = int(params.get(MACD_SLOW, 26))
            signal_period = int(params.get(MACD_SIGNAL, 9))
            operation_type = params.get(OPERATION_TYPE, SIGNAL_BUY)
        except (ValueError, TypeError):
            print("Invalid parameter types for MACDCross indicator.")
            return SIGNAL_HOLD

        # --- 2. Data Validation ---
        # MACD requires at least 'slow' + 'signal' periods for a stable calculation
        if len(data) < (slow + signal_period) or CLOSE_COLUMN not in data.columns:
            return SIGNAL_HOLD

        # --- 3. Indicator Calculation ---
        # pandas_ta returns a DataFrame with MACD_12_26_9, MACDs_12_26_9, MACDh_12_26_9
        macd_df = ta.macd(data[CLOSE_COLUMN], fast=fast, slow=slow, signal=signal_period)
        
        if macd_df is None or macd_df.empty:
            return SIGNAL_HOLD

        # Identify column names based on parameters
        macd_col = f"MACD_{fast}_{slow}_{signal_period}"
        signal_col = f"MACDs_{fast}_{slow}_{signal_period}"

        # Get values for current bar (-1) and previous bar (-2)
        curr_macd = macd_df[macd_col].iloc[-1]
        curr_signal = macd_df[signal_col].iloc[-1]
        
        prev_macd = macd_df[macd_col].iloc[-2]
        prev_signal = macd_df[signal_col].iloc[-2]

        # --- 4. Crossover Logic ---
        if operation_type == SIGNAL_BUY:
            # Bullish Cross: MACD was below Signal and is now above
            if prev_macd <= prev_signal and curr_macd > curr_signal:
                print("MACD crossed above Signal line.")
                return SIGNAL_BUY
                
        elif operation_type == SIGNAL_SELL:
            # Bearish Cross: MACD was above Signal and is now below
            if prev_macd >= prev_signal and curr_macd < curr_signal:
                print("MACD crossed below Signal line.")
                return SIGNAL_SELL

        return SIGNAL_HOLD