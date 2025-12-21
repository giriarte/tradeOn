import pandas_ta as ta
import typing as t

from indicators.constants import ( 
    OPERATION_TYPE,
    SIGNAL_BUY,
    SIGNAL_HOLD,
    SIGNAL_SELL
)
from .indicator import Indicator

class Doji(Indicator):
    """
    A Doji candlestick forms when a security's open and close are virtually equal. 
    The pattern resembles a cross or plus sign and signifies indecision between 
    buyers and sellers. 
    
    This class returns a signal based on the 'operationType' provided in params:
    - If operationType is 'buy', returns SIGNAL_BUY when a Doji is detected.
    - If operationType is 'sell', returns SIGNAL_SELL when a Doji is detected.
    """

    def evaluate(self, df: t.Any, params: t.Optional[t.Dict[str, t.Any]] = None) -> int:
        return_signal = SIGNAL_HOLD
        
        # Use instance parameters if none are provided
        if (params is None):
            params = self.params

        # Default to 'buy' if no operationType is provided, or handle as needed
        operation_type = params.get(OPERATION_TYPE, SIGNAL_BUY) if params else SIGNAL_BUY
        
        # Calculate Doji pattern (returns 100 when a Doji is identified)
        doji_value = ta.cdl_pattern(df["Open"], df["High"], df["Low"], df["Close"], name="doji")
        
        if doji_value is not None and not doji_value.empty:
            # Extract the last signal (Doji is 100, no pattern is 0)
            last_signal = doji_value.iloc[-1].values[0]
            
            if last_signal == 100:
                print(f"Doji detected at {df.index[-1]} - Executing {operation_type}")
                
                return_signal = operation_type

        return return_signal