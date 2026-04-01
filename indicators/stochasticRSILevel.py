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

class StochasticRSILevel(Indicator):
    """
    Emits a signal when the Stochastic RSI K-line crosses a defined threshold.
    
    Parameters:
    - 'rsi_length': (int) Period for the RSI calculation (default 14).
    - 'stoch_length': (int) Period for the Stochastic calculation (default 14).
    - 'k_period': (int) Smoothing for the K line (default 3).
    - 'd_period': (int) Smoothing for the D line (default 3).
    - 'threshold': (float) The level to check against (e.g., 20.0 for BUY, 80.0 for SELL).
    - 'operation_type': (int) SIGNAL_BUY (triggers if StochRSI < threshold)
                             SIGNAL_SELL (triggers if StochRSI > threshold).
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
            threshold = float(params.get(THRESHOLD, 20.0))
            operation_type = int(params.get(OPERATION_TYPE, SIGNAL_BUY))
        except (ValueError, TypeError):
            print("Invalid parameters provided to StochasticRSILevel indicator.")
            return SIGNAL_HOLD

        # --- 2. Data Validation ---
        # StochRSI needs enough data for the RSI plus the Stoch lookback
        if len(data) < (rsi_len + stoch_len) or CLOSE_COLUMN not in data.columns:
            return SIGNAL_HOLD

        # --- 3. Indicator Calculation ---
        # pandas_ta returns a DataFrame with STOCHRSIk_14_14_3_3 and STOCHRSId_14_14_3_3
        stoch_rsi_df = ta.stochrsi(
            data[CLOSE_COLUMN], 
            length=stoch_len, 
            rsi_length=rsi_len, 
            k=k_smoothing, 
            d=d_smoothing
        )
        
        if stoch_rsi_df is None or stoch_rsi_df.empty:
            return SIGNAL_HOLD

        # Target the %K line for the signal
        k_col = f"STOCHRSIk_{stoch_len}_{rsi_len}_{k_smoothing}_{d_smoothing}"
        current_k = stoch_rsi_df[k_col].iloc[-1]

        # --- 4. Level Logic ---
        if operation_type == SIGNAL_BUY:
            # Oversold: Price momentum is low, looking for a bounce
            if current_k < threshold:
                print( "StochasticRSILevel: BUY signal triggered." )
                return SIGNAL_BUY
                
        elif operation_type == SIGNAL_SELL:
            # Overbought: Price momentum is high, looking for a reversal
            if current_k > threshold:
                print( "StochasticRSILevel: SELL signal triggered." )
                return SIGNAL_SELL

        return SIGNAL_HOLD