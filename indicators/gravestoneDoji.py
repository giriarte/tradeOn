import pandas_ta as ta
import typing as t

from indicators.constants import ( 
    CLOSE_COLUMN,
    HIGH_COLUMN,
    LOW_COLUMN,
    OPEN_COLUMN,
    SIGNAL_HOLD,
    SIGNAL_SELL
)
from .indicator import Indicator

class GravestoneDoji(Indicator):
    """
    A Gravestone Doji is a single-candle pattern that forms when the 
    Open, Low, and Close are equal or very close to each other at the Low of the day.
    
    - Signifies: Potential bearish reversal. The long upper shadow indicates that 
      the market tested a high resistance level only to be rejected by sellers.
    
    This class returns:
    - SIGNAL_SELL if a Gravestone Doji is detected (value 100).
    - SIGNAL_HOLD otherwise.
    """

    def evaluate(self, df: t.Any, params: t.Optional[t.Dict[str, t.Any]] = None) -> int:
        return_signal = SIGNAL_HOLD
        
        # Use instance parameters if none are provided
        if params is None:
            params = self.params

        # Calculate Gravestone Doji pattern using pandas_ta
        # Note: pandas_ta returns 100 for this bullish-to-bearish reversal pattern
        doji_series = ta.cdl_pattern(
            df[OPEN_COLUMN], 
            df[HIGH_COLUMN], 
            df[LOW_COLUMN], 
            df[CLOSE_COLUMN], 
            name="gravestonedoji"
        )
        
        if doji_series is not None and not doji_series.empty:
            # Extract the last signal
            last_signal = doji_series.iloc[-1].values[0]
            
            # While the value is 100 (pattern found), it indicates a Bearish signal
            if last_signal == 100:
                print(f"Gravestone Doji detected at {df.index[-1]}")
                return_signal = SIGNAL_SELL

        return return_signal