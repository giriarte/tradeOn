import pandas as pd
import typing as t
from .indicator import Indicator
from indicators.constants import (
    SIGNAL_BUY,
    SIGNAL_HOLD
)

# Assuming VOLUME_COLUMN is defined in your constants, otherwise use 'Volume'
VOLUME_COLUMN = 'Volume' 

class VolumeBreakout(Indicator):
    """
    Checks if the current volume is greater than the average volume of the 
    previous N candles by a specific percentage.
    
    Parameters:
    - 'volume_lookback': (int) Number of previous candles to average (default 20).
    - 'increase_pct': (float) Percentage increase required (e.g., 50.0 for 50% above avg).
    - 'operation_type': (int) Signal to return if condition is met (default SIGNAL_BUY).
    """

    def evaluate(self, data: pd.DataFrame, params: t.Optional[t.Dict[str, t.Any]] = None) -> int:
        if params is None:
            params = self.params

        # --- 1. Parameter Extraction ---
        try:
            lookback = int(params.get('volume_lookback', 20))
            increase_pct = float(params.get('increase_pct', 50.0))
            operation_type = int(params.get('operation_type', SIGNAL_BUY))
        except (ValueError, TypeError):
            print("VolumeBreakout: Invalid parameter types.")
            return SIGNAL_HOLD

        # --- 2. Data Validation ---
        # We need lookback + 1 (the current candle)
        if len(data) < (lookback + 1) or VOLUME_COLUMN not in data.columns:
            return SIGNAL_HOLD

        # --- 3. Logic Execution ---
        # Get historical volume excluding the current candle
        historical_volume = data[VOLUME_COLUMN].iloc[-(lookback + 1):-1]
        avg_volume = historical_volume.mean()

        if avg_volume <= 0:
            return SIGNAL_HOLD

        current_volume = data[VOLUME_COLUMN].iloc[-1]
        
        # Calculate percentage increase over average
        # Formula: ((Current / Average) - 1) * 100
        vol_increase = ((current_volume / avg_volume) - 1) * 100

        if vol_increase >= increase_pct:
            print(f"VolumeBreakout: Current volume {current_volume} is {vol_increase:.2f}% above average {avg_volume}.")
            return operation_type

        return SIGNAL_HOLD