import pandas_ta as ta
import typing as t

from indicators.constants import ( 
    SIGNAL_BUY,
    SIGNAL_HOLD,
    SIGNAL_SELL
)
from .indicator import Indicator

class EveningStar(Indicator):
    """
    The evening star pattern consists of three distinct candlesticks that indicate a reversal in market sentiment 
    from bullish to bearish. It forms after an uptrend and is characterized by the following components:

    First Candle: A long bullish (green) candlestick that continues the existing uptrend, reflecting strong buying pressure.

    Second Candle: A smaller-bodied candle (which can be bullish or bearish) that gaps up from the first candle's close. 
    This candle represents indecision in the market, as the upward momentum stalls. It often resembles a doji or spinning top.

    Third Candle: A long bearish (red) candlestick that opens below the second candle and closes significantly lower 
    (usually at least halfway into the body of the first candle), 
    confirming the reversal and indicating that sellers have taken control.
    """

    def evaluate(self, df: t.Any, params: t.Optional[t.Dict[str, t.Any]] = None) -> int:
        return_signal = SIGNAL_HOLD
        
        # Use the 'eveningstar' pattern
        eveningStarValue = ta.cdl_pattern(df["Open"], df["High"], df["Low"], df["Close"], name="eveningstar")
        
        # Extract the last value
        # TA-Lib returns -100 for a bearish signal
        if eveningStarValue is not None and not eveningStarValue.empty:
            last_signal = eveningStarValue.iloc[-1].values[0]
            
            # We check for < 0 or specifically == -100
            if last_signal is not None and last_signal < 0:
                print(f"Evening Star detected at {df.index[-1]}")
                return_signal = SIGNAL_SELL if last_signal == -100 else SIGNAL_HOLD

        return return_signal
