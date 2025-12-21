import typing as t

from indicators.doji import Doji
from indicators.eveningStar import EveningStar
from indicators.indicator import Indicator
from indicators.morningStar import MorningStar
from indicators.nGreenCandles import NGreenCandles
from indicators.nRedCandles import NRedCandles
from indicators.rsi import RSI

# --- Indicator Registry ---
# Map the string name in DynamoDB to the class implementation
INDICATOR_MAP = {
    "NGreenCandles": NGreenCandles,
    "NRedCandles": NRedCandles,
    "RSI": RSI,
    "MorningStar": MorningStar,
    "EveningStar": EveningStar,
    "Doji": Doji
}

def get_indicator_instance(name: str, all_params: dict) -> Indicator:
    indicator_class = INDICATOR_MAP.get(name)
    if not indicator_class:
        raise ValueError(f"Indicator implementation for '{name}' not found.")
    
    # Extract specific params for this indicator
    specific_params = all_params.get(name, {})
    
    print(f"Creating indicator '{name}' with params: {specific_params}")
    return indicator_class(name=name, params=specific_params)