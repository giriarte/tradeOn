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

class HangingMan(Indicator):
    """
    A Hanging Man is a single-candle bearish reversal pattern.
    - It occurs at the top of an uptrend.
    - It has a small real body and a long lower shadow (at least 2x the body).
    - This implementation only triggers if the candle is RED (Close < Open).

    This class returns:
    - SIGNAL_SELL if a Red Hanging Man is detected.
    - SIGNAL_HOLD otherwise.
    """

    def evaluate(self, df: t.Any, params: t.Optional[t.Dict[str, t.Any]] = None) -> int:
        return_signal = SIGNAL_HOLD
        
        # Use instance parameters if none are provided
        if params is None:
            params = self.params

        # Calculate Hanging Man pattern using pandas_ta
        # Note: pandas_ta returns -100 for this bearish reversal pattern
        hanging_man_series = ta.cdl_pattern(
            df[OPEN_COLUMN], 
            df[HIGH_COLUMN], 
            df[LOW_COLUMN], 
            df[CLOSE_COLUMN], 
            name="hangingman"
        )
        
        if hanging_man_series is not None and not hanging_man_series.empty:
            # Extract the last signal
            last_signal = hanging_man_series.iloc[-1].values[0]
            
            # Check if the pattern was found (-100 for bearish)
            if last_signal == -100:
                # Extract OHLC for the most recent candle
                last_open = df[OPEN_COLUMN].iloc[-1]
                last_close = df[CLOSE_COLUMN].iloc[-1]
                
                # Filter: Only accept if the candle is red
                if last_close < last_open:
                    print(f"Red Hanging Man detected at {df.index[-1]}")
                    return_signal = SIGNAL_SELL

        return return_signal