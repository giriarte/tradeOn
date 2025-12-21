import pandas_ta as ta
import typing as t

from indicators.constants import ( 
    SIGNAL_BUY,
    SIGNAL_HOLD,
    SIGNAL_SELL
)
from .indicator import Indicator

class Harami(Indicator):
    """
    A Harami pattern is a two-candle reversal pattern where a small candle 
    is contained within the body of the previous large candle.
    - Bullish Harami: Occurs in a downtrend; a small green candle inside a large red candle.
    - Bearish Harami: Occurs in an uptrend; a small red candle inside a large green candle.

    This class returns a signal based on the pattern detected:
    - If a Bullish Harami is detected (value 100), returns SIGNAL_BUY.
    - If a Bearish Harami is detected (value -100), returns SIGNAL_SELL.
    """

    def evaluate(self, df: t.Any, params: t.Optional[t.Dict[str, t.Any]] = None) -> int:
        return_signal = SIGNAL_HOLD
        
        # Use instance parameters if none are provided
        if params is None:
            params = self.params

        # Calculate Harami pattern using pandas_ta
        # Note: pandas_ta uses TA-Lib logic which returns 100 for Bullish and -100 for Bearish
        harami_series = ta.cdl_pattern(
            df["Open"], 
            df["High"], 
            df["Low"], 
            df["Close"], 
            name="harami"
        )
        
        if harami_series is not None and not harami_series.empty:
            # Extract the last signal from the resulting DataFrame
            # Column name is typically "CDL_HARAMI"
            last_signal = harami_series.iloc[-1].values[0]
            
            if last_signal == 100:
                print(f"Bullish Harami detected at {df.index[-1]}")
                return_signal = SIGNAL_BUY
            elif last_signal == -100:
                print(f"Bearish Harami detected at {df.index[-1]}")
                return_signal = SIGNAL_SELL

        return return_signal