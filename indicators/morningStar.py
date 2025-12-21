import pandas_ta as ta
import typing as t

from indicators.constants import ( 
    RSI_COLUMN,
    RSI_LENGTH,
    RSI_SELL_THRESHOLD,
    SIGNAL_BUY,
    SIGNAL_HOLD,
    SIGNAL_SELL
)
from .indicator import Indicator

class MorningStar(Indicator):
    """
    The morning star pattern consists of three distinct candlesticks that indicate a reversal in market sentiment 
    from bearish to bullish. It forms after a downtrend and is characterized by the following components:
        First Candle: A long bearish (red) candlestick that continues the existing downtrend, reflecting strong selling pressure.
        Second Candle: A smaller-bodied candle (which can be bullish or bearish) that gaps down from the first candle's close.
          This candle represents indecision in the market, as buyers and sellers are battling for control. It often resembles a doji or spinning top.
        Third Candle: A long bullish (green) candlestick that opens above the second candle and closes significantly higher, 
          confirming the reversal and indicating that buyers have taken control.
    """

    def evaluate(self, df: t.Any, params: t.Optional[t.Dict[str, t.Any]] = None) -> int:
        return_signal = SIGNAL_HOLD
        morningStarValue = ta.cdl_pattern(df["Open"], df["High"], df["Low"], df["Close"], name="morningstar")
        
        # Extract the last value
        # TA-Lib returns 100 for a bullish signal; we convert it to 1
        if morningStarValue is not None and not morningStarValue.empty:
            last_signal = morningStarValue.iloc[-1].values[0]
            if last_signal is not None and last_signal > 0:
                print(f"Morning Star detected at {df.index[-1]}")
            return_signal = SIGNAL_BUY if last_signal == 100 else SIGNAL_HOLD

        return return_signal
