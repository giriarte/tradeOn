import typing as t

from indicators.InvertedHammer import InvertedHammer
from indicators.aboveEMA import AboveEMA
from indicators.adxRange import ADXRange
from indicators.bearishCandlePattern import BearishCandlePattern
from indicators.belowEMA import BelowEMA
from indicators.bollingerBandReEntry import BollingerBandReEntry
from indicators.bollingerBandWidth import BollingerBandWidth
from indicators.bullishCandlePattern import BullishCandlePattern
from indicators.closePrice import ClosePrice
from indicators.customCandle import CustomCandle
from indicators.dmnRange import DMNRange
from indicators.dmpRange import DMPRange
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
from indicators.longCandle import LongCandle
from indicators.macdCross import MACDCross
from indicators.macdDivergence import MACDDivergence
from indicators.morningStar import MorningStar
from indicators.nGreenCandles import NGreenCandles
from indicators.nRedCandles import NRedCandles
from indicators.nearEma import NearEMA
from indicators.nearResistance import NearResistance
from indicators.nearSupport import NearSupport
from indicators.priceAboveBollingerBand import PriceAboveBollingerBand
from indicators.priceBelowBolingerBand import PriceBelowBollingerBand
from indicators.rsi import RSI
from indicators.shootingStar import ShootingStar
from indicators.stochasticRSICross import StochasticRSICross
from indicators.stochasticRSILevel import StochasticRSILevel
from indicators.volumeBreakout import VolumeBreakout

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
    "BollingerBandReEntry": BollingerBandReEntry,
    "BollingerBandWidth": BollingerBandWidth,
    "PriceBelowBollingerBand": PriceBelowBollingerBand,
    "PriceAboveBollingerBand": PriceAboveBollingerBand,
    "NearSupport": NearSupport,
    "NearEMA": NearEMA,
    "NearResistance": NearResistance,
    "ClosePrice": ClosePrice,
    "MACDCross": MACDCross,
    "MACDDivergence": MACDDivergence,
    "StochasticRSILevel": StochasticRSILevel,
    "StochasticRSICross": StochasticRSICross,
    "ADXRange": ADXRange,
    "DMPRange": DMPRange,
    "DMNRange": DMNRange,
    "BelowEMA": BelowEMA,
    "AboveEMA": AboveEMA,
    "VolumeBreakout": VolumeBreakout,
    "LongCandle": LongCandle,
    "CustomCandle": CustomCandle
}

def get_indicator_instance(name: str, all_params: dict, offset: int | None) -> Indicator:
    indicator_class = INDICATOR_MAP.get(name)
    if not indicator_class:
        raise ValueError(f"Indicator implementation for '{name}' not found.")
    
    # Extract specific params for this indicator
    specific_params = all_params.get(name, {})
    
    print(f"Creating indicator '{name}' with params: {specific_params}")
    return indicator_class(name=name, params=specific_params, offset=offset)