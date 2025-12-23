import typing as t

from indicators.InvertedHammer import InvertedHammer
from indicators.bearishCandlePattern import BearishCandlePattern
from indicators.bollingerBandReEntry import BollingerBandReEntry
from indicators.bullishCandlePattern import BullishCandlePattern
from indicators.doji import Doji
from indicators.dragonFlyDoji import DragonflyDoji
from indicators.emaCross import EMACross
from indicators.emaDistanceCap import EMADistanceCap
from indicators.emaSlope import EMASlope
from indicators.engulfing import Engulfing
from indicators.eveningStar import EveningStar
from indicators.gravestoneDoji import GravestoneDoji
from indicators.hammer import Hammer
from indicators.hangingMan import HangingMan
from indicators.harami import Harami
from indicators.indicator import Indicator
from indicators.morningStar import MorningStar
from indicators.nGreenCandles import NGreenCandles
from indicators.nRedCandles import NRedCandles
from indicators.rsi import RSI
from indicators.shootingStar import ShootingStar

# --- Indicator Registry ---
# Map the string name in DynamoDB to the class implementation
INDICATOR_MAP = {
    "NGreenCandles": NGreenCandles,
    "NRedCandles": NRedCandles,
    "RSI": RSI,
    "MorningStar": MorningStar,
    "EveningStar": EveningStar,
    "Doji": Doji,
    "Engulfing": Engulfing,
    "Harami": Harami,
    "DragonflyDoji": DragonflyDoji,
    "GravestoneDoji": GravestoneDoji,
    "Hammer": Hammer,
    "InvertedHammer": InvertedHammer,
    "ShootingStar": ShootingStar,
    "HangingMan": HangingMan,
    "BullishCandlePattern": BullishCandlePattern,
    "BearishCandlePattern": BearishCandlePattern,
    "EMADistanceCap": EMADistanceCap,
    "EMASlope": EMASlope,
    "EMACross": EMACross,
    "BollingerBandReEntry": BollingerBandReEntry
}

def get_indicator_instance(name: str, all_params: dict) -> Indicator:
    indicator_class = INDICATOR_MAP.get(name)
    if not indicator_class:
        raise ValueError(f"Indicator implementation for '{name}' not found.")
    
    # Extract specific params for this indicator
    specific_params = all_params.get(name, {})
    
    print(f"Creating indicator '{name}' with params: {specific_params}")
    return indicator_class(name=name, params=specific_params)