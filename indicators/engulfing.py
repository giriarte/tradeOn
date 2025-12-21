import pandas_ta as ta
import typing as t

from indicators.constants import ( 
    SIGNAL_BUY,
    SIGNAL_HOLD,
    SIGNAL_SELL
)
from .indicator import Indicator

class Engulfing(Indicator):
    """
    An Engulfing pattern is a two-candle reversal pattern. 
    - Bullish Engulfing: Appears in a downtrend, signaling a potential reversal to the upside.
    - Bearish Engulfing: Appears in an uptrend, signaling a potential reversal to the downside.

    This class returns a signal based on the pattern detected:
    - If a Bullish Engulfing is detected (value 100), returns SIGNAL_BUY.
    - If a Bearish Engulfing is detected (value -100), returns SIGNAL_SELL.
    """

    def evaluate(self, df: t.Any, params: t.Optional[t.Dict[str, t.Any]] = None) -> int:
        return_signal = SIGNAL_HOLD
        
        # Use instance parameters if none are provided
        if params is None:
            params = self.params

        # Calculate Engulfing pattern using pandas_ta
        # This returns 100 for Bullish and -100 for Bearish
        engulfing_series = ta.cdl_pattern(df["Open"], df["High"], df["Low"], df["Close"], name="engulfing")
        
        if engulfing_series is not None and not engulfing_series.empty:
            # Extract the last signal from the resulting DataFrame
            last_signal = engulfing_series.iloc[-1].values[0]
            
            if last_signal == 100:
                print(f"Bullish Engulfing detected at {df.index[-1]}")
                return_signal = SIGNAL_BUY
            elif last_signal == -100:
                print(f"Bearish Engulfing detected at {df.index[-1]}")
                return_signal = SIGNAL_SELL

        return return_signal