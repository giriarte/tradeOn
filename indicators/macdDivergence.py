import pandas_ta as ta
import pandas as pd
import typing as t
from .indicator import Indicator
from indicators.constants import (
    CLOSE_COLUMN,
    LOOKBACK,
    LOW_COLUMN,
    HIGH_COLUMN,
    OPERATION_TYPE,
    SIGNAL_BUY,
    SIGNAL_SELL,
    SIGNAL_HOLD,
    MACD_FAST,
    MACD_SIGNAL,
    MACD_SLOW
)

class MACDDivergence(Indicator):
    """
    Detects Bullish or Bearish divergence between Price and the MACD line.
    
    Parameters:
    - 'macd_fast', 'macd_slow', 'macd_signal': MACD periods (default 12, 26, 9).
    - 'lookback': How many candles to look back for the previous peak/trough (default 20).
    - 'operation_type': SIGNAL_BUY (Bullish Divergence) or SIGNAL_SELL (Bearish Divergence).
    """

    def evaluate(self, data: pd.DataFrame, params: t.Optional[t.Dict[str, t.Any]] = None) -> int:
        if params is None:
            params = self.params

        # --- 1. Parameter Extraction ---
        try:
            fast = int(params.get(MACD_FAST, 12))
            slow = int(params.get(MACD_SLOW, 26))
            signal_period = int(params.get(MACD_SIGNAL, 9))
            lookback = int(params.get(LOOKBACK, 20))
            operation_type = int(params.get(OPERATION_TYPE, SIGNAL_BUY))
        except (ValueError, TypeError):
            print("Invalid parameter types for MACDDivergence indicator.")
            return SIGNAL_HOLD

        # --- 2. Data Validation ---
        if len(data) < (slow + lookback) or CLOSE_COLUMN not in data.columns:
            return SIGNAL_HOLD

        # --- 3. Indicator Calculation ---
        macd_df = ta.macd(data[CLOSE_COLUMN], fast=fast, slow=slow, signal=signal_period)
        if macd_df is None or macd_df.empty:
            return SIGNAL_HOLD

        macd_col = f"MACD_{fast}_{slow}_{signal_period}"
        macd_series = macd_df[macd_col]

        # --- 4. Divergence Logic ---
        # Get current values
        curr_price_high = data[HIGH_COLUMN].iloc[-1]
        curr_price_low = data[LOW_COLUMN].iloc[-1]
        curr_macd = macd_series.iloc[-1]

        # Get historical window (excluding current candle)
        hist_price_highs = data[HIGH_COLUMN].iloc[-(lookback + 1):-1]
        hist_price_lows = data[LOW_COLUMN].iloc[-(lookback + 1):-1]
        hist_macd = macd_series.iloc[-(lookback + 1):-1]

        if operation_type == SIGNAL_BUY:
            # Bullish Divergence: Price makes a Lower Low, but MACD makes a Higher Low
            prev_low_price = hist_price_lows.min()
            # Find the MACD value at that previous price low
            idx_prev_low = hist_price_lows.idxmin()
            prev_low_macd = macd_series.loc[idx_prev_low]

            if curr_price_low < prev_low_price and curr_macd > prev_low_macd:
                print(f"MACD Divergence: Bullish - Price Low: {curr_price_low}, MACD Low: {curr_macd}")
                return SIGNAL_BUY

        elif operation_type == SIGNAL_SELL:
            # Bearish Divergence: Price makes a Higher High, but MACD makes a Lower High
            prev_high_price = hist_price_highs.max()
            # Find the MACD value at that previous price high
            idx_prev_high = hist_price_highs.idxmax()
            prev_high_macd = macd_series.loc[idx_prev_high]

            if curr_price_high > prev_high_price and curr_macd < prev_high_macd:
                print(f"MACD Divergence: Bearish - Price High: {curr_price_high}, MACD High: {curr_macd}")
                return SIGNAL_SELL

        return SIGNAL_HOLD