import pandas_ta as ta
import typing as t

from indicators.constants import ( 
    SIGNAL_BUY,
    SIGNAL_HOLD
)
from .indicator import Indicator

class InvertedHammer(Indicator):
    """
    An Inverted Hammer is a single-candle bullish reversal pattern.
    - It occurs at the bottom of a downtrend.
    - This specific implementation only triggers if the candle is GREEN 
      (Close > Open), indicating stronger bullish sentiment.

    This class returns:
    - SIGNAL_BUY if a Green Inverted Hammer is detected.
    - SIGNAL_HOLD otherwise.
    """

    def evaluate(self, df: t.Any, params: t.Optional[t.Dict[str, t.Any]] = None) -> int:
        return_signal = SIGNAL_HOLD
        
        # Use instance parameters if none are provided
        if params is None:
            params = self.params

        # Calculate Inverted Hammer pattern using pandas_ta
        inv_hammer_series = ta.cdl_pattern(
            df["Open"], 
            df["High"], 
            df["Low"], 
            df["Close"], 
            name="invertedhammer"
        )
        
        if inv_hammer_series is not None and not inv_hammer_series.empty:
            # Extract the last signal from the resulting DataFrame
            last_signal = inv_hammer_series.iloc[-1].values[0]
            
            # Check if the pattern was found (100)
            if last_signal == 100:
                # Extract OHLC for the most recent candle
                last_open = df["Open"].iloc[-1]
                last_close = df["Close"].iloc[-1]
                
                # Filter: Only accept the signal if the candle is green
                if last_close > last_open:
                    print(f"Green Inverted Hammer detected at {df.index[-1]}")
                    return_signal = SIGNAL_BUY

        return return_signal