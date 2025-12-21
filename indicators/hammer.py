import pandas_ta as ta
import typing as t

from indicators.constants import ( 
    SIGNAL_BUY,
    SIGNAL_HOLD
)
from .indicator import Indicator

class Hammer(Indicator):
    """
    A Hammer is a single-candle bullish reversal pattern.
    - It occurs during a downtrend.
    - It has a small real body and a long lower shadow (wick).
    - The lower shadow should be at least two times the height of the body.

    This class returns:
    - SIGNAL_BUY if a Hammer is detected (value 100).
    - SIGNAL_HOLD otherwise.
    """

    def evaluate(self, df: t.Any, params: t.Optional[t.Dict[str, t.Any]] = None) -> int:
        return_signal = SIGNAL_HOLD
        
        if params is None:
            params = self.params

        hammer_series = ta.cdl_pattern(df["Open"], df["High"], df["Low"], df["Close"], name="hammer")
        
        if hammer_series is not None and not hammer_series.empty:
            last_signal = hammer_series.iloc[-1].values[0]
            
            if last_signal == 100:
                # Get the last candle's OHLC
                last_open = df["Open"].iloc[-1]
                last_close = df["Close"].iloc[-1]
                
                # Check if it's a Green candle (Close > Open)
                if last_close > last_open:
                    print(f"Strong Bullish (Green) Hammer detected at {df.index[-1]}")
                    return_signal = SIGNAL_BUY

        return return_signal