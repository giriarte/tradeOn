import pandas_ta as ta
import pandas as pd
import typing as t
from .indicator import Indicator
from indicators.constants import (
    CLOSE_COLUMN,
    D_PERIOD,
    K_PERIOD,
    OPERATION_TYPE,
    RSI_LENGTH,
    SIGNAL_BUY,
    SIGNAL_SELL,
    SIGNAL_HOLD,
    STOCH_LENGTH,
    THRESHOLD
)

class StochasticRSICross(Indicator):
    """
    Detects a crossover between Stochastic RSI %K and %D lines.
    
    Parameters:
    - 'rsi_length', 'stoch_length': Periods for calculation (default 14).
    - 'k_period', 'd_period': Smoothing for K and D lines (default 3).
    - 'threshold': (float, optional) Only trigger if cross happens below this (BUY) 
                   or above this (SELL). Set to None to ignore.
    - 'operation_type': (int) SIGNAL_BUY (K crosses ABOVE D)
                             SIGNAL_SELL (K crosses BELOW D).
    """

    def evaluate(self, data: pd.DataFrame, params: t.Optional[t.Dict[str, t.Any]] = None) -> int:
        if params is None:
            params = self.params

        # --- 1. Parameter Extraction ---
        try:
            rsi_len = int(params.get(RSI_LENGTH, 14))
            stoch_len = int(params.get(STOCH_LENGTH, 14))
            k_smoothing = int(params.get(K_PERIOD, 3))
            d_smoothing = int(params.get(D_PERIOD, 3))
            threshold = params.get(THRESHOLD)
            operation_type = int(params.get(OPERATION_TYPE, SIGNAL_BUY))
        except (ValueError, TypeError):
            print("Invalid parameters provided to StochasticRSICross indicator.")
            return SIGNAL_HOLD

        # --- 2. Data Validation ---
        if len(data) < (rsi_len + stoch_len + 2) or CLOSE_COLUMN not in data.columns:
            return SIGNAL_HOLD

        # --- 3. Indicator Calculation ---
        stoch_rsi_df = ta.stochrsi(
            data[CLOSE_COLUMN], 
            length=stoch_len, 
            rsi_length=rsi_len, 
            k=k_smoothing, 
            d=d_smoothing
        )
        
        if stoch_rsi_df is None or stoch_rsi_df.empty:
            return SIGNAL_HOLD

        k_col = f"STOCHRSIk_{stoch_len}_{rsi_len}_{k_smoothing}_{d_smoothing}"
        d_col = f"STOCHRSId_{stoch_len}_{rsi_len}_{k_smoothing}_{d_smoothing}"

        # Current values
        curr_k = stoch_rsi_df[k_col].iloc[-1]
        curr_d = stoch_rsi_df[d_col].iloc[-1]
        
        # Previous values
        prev_k = stoch_rsi_df[k_col].iloc[-2]
        prev_d = stoch_rsi_df[d_col].iloc[-2]

        # --- 4. Crossover Logic ---
        if operation_type == SIGNAL_BUY:
            # Bullish Cross: K moves from below D to above D
            if prev_k <= prev_d and curr_k > curr_d:
                # Optional threshold check (e.g., cross must happen below 20)
                if threshold is not None and curr_k > float(threshold):
                    return SIGNAL_HOLD
                print( "StochasticRSICross: BUY signal triggered." )
                return SIGNAL_BUY
                
        elif operation_type == SIGNAL_SELL:
            # Bearish Cross: K moves from above D to below D
            if prev_k >= prev_d and curr_k < curr_d:
                # Optional threshold check (e.g., cross must happen above 80)
                if threshold is not None and curr_k < float(threshold):
                    return SIGNAL_HOLD
                print( "StochasticRSICross: SELL signal triggered." )
                return SIGNAL_SELL

        return SIGNAL_HOLD