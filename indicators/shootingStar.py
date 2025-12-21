import pandas_ta as ta
import typing as t

from indicators.constants import ( 
    SIGNAL_HOLD,
    SIGNAL_SELL
)
from .indicator import Indicator

class ShootingStar(Indicator):
    """
    A Shooting Star is a single-candle bearish reversal pattern.
    - It occurs at the peak of an uptrend.
    - It has a long upper shadow (at least 2x the body) and a small real body.
    - This implementation only triggers if the candle is RED (Close < Open).

    This class returns:
    - SIGNAL_SELL if a Red Shooting Star is detected.
    - SIGNAL_HOLD otherwise.
    """

    def evaluate(self, df: t.Any, params: t.Optional[t.Dict[str, t.Any]] = None) -> int:
        return_signal = SIGNAL_HOLD
        
        # Use instance parameters if none are provided
        if params is None:
            params = self.params

        # Calculate Shooting Star pattern using pandas_ta
        # Returns -100 for a bearish pattern detection
        star_series = ta.cdl_pattern(
            df["Open"], 
            df["High"], 
            df["Low"], 
            df["Close"], 
            name="shootingstar"
        )
        
        if star_series is not None and not star_series.empty:
            # Extract the last signal
            last_signal = star_series.iloc[-1].values[0]
            
            # pandas_ta returns -100 for Shooting Star
            if last_signal == -100:
                # Extract OHLC for the most recent candle
                last_open = df["Open"].iloc[-1]
                last_close = df["Close"].iloc[-1]
                
                # Filter: Only accept if the candle is red (Bearish confirmation)
                if last_close < last_open:
                    print(f"Red Shooting Star detected at {df.index[-1]}")
                    return_signal = SIGNAL_SELL

        return return_signal