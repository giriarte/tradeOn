import pandas_ta as ta
import typing as t

from indicators.constants import ( 
    SIGNAL_BUY,
    SIGNAL_HOLD
)
from .indicator import Indicator

class DragonflyDoji(Indicator):
    """
    A Dragonfly Doji is a single-candle pattern that forms when the 
    Open, High, and Close are equal or very close to each other at the High of the day.
    
    - Signifies: Potential bullish reversal, as sellers pushed prices down significantly 
      but buyers regained control to close back at the high.
    
    This class returns:
    - SIGNAL_BUY if a Dragonfly Doji is detected (value 100).
    - SIGNAL_HOLD otherwise.
    """

    def evaluate(self, df: t.Any, params: t.Optional[t.Dict[str, t.Any]] = None) -> int:
        return_signal = SIGNAL_HOLD
        
        # Use instance parameters if none are provided
        if params is None:
            params = self.params

        # Calculate Dragonfly Doji pattern using pandas_ta
        # Returns 100 when detected
        doji_series = ta.cdl_pattern(
            df["Open"], 
            df["High"], 
            df["Low"], 
            df["Close"], 
            name="dragonflydoji"
        )
        
        if doji_series is not None and not doji_series.empty:
            # Extract the last signal
            last_signal = doji_series.iloc[-1].values[0]
            
            if last_signal == 100:
                print(f"Dragonfly Doji detected at {df.index[-1]}")
                return_signal = SIGNAL_BUY

        return return_signal