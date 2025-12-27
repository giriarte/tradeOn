import typing as t
from indicators.InvertedHammer import InvertedHammer
from indicators.adxRange import ADXRange
from indicators.bearishCandlePattern import BearishCandlePattern
from indicators.bollingerBandReEntry import BollingerBandReEntry
from indicators.bollingerBandWidth import BollingerBandWidth
from indicators.bullishCandlePattern import BullishCandlePattern
from indicators.closePrice import ClosePrice
from indicators.constants import (
    DISTANCE_PCT_CAP,
    EMA_LENGTH,
    N_CANDLES_LENGTH,
    N_CANDLES_OFFSET,
    N_CANDLES_OPERATION,
    OPERATION_TYPE, 
    RSI_BUY_THRESHOLD, 
    RSI_LENGTH, 
    RSI_SELL_THRESHOLD
)
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
from indicators.macdCross import MACDCross
from indicators.macdDivergence import MACDDivergence
from indicators.morningStar import MorningStar
from indicators.nGreenCandles import NGreenCandles
from indicators.nearEma import NearEMA
from indicators.nearSupport import NearSupport
from indicators.rsi import RSI
from indicators.shootingStar import ShootingStar
from indicators.stochasticRSICross import StochasticRSICross
from indicators.stochasticRSILevel import StochasticRSILevel
from strategies.strategy import TradeStrategy, Position

Dictionary = t.Dict[str, t.Dict[str, t.Any]] # Represents the default parameters map

class ThreeGreenCandlesRsi(TradeStrategy):
    rsiLength = 10
    rsiBuyThreshold = 30
    rsiSellThreshold = 70
    nCandlesLength = 3
    nCandlesOperation = 2
    nCandlesOffset = 1

    # --- ATTRIBUTES (Class Variables or Properties for definition) ---
    name: str = 'ThreeGreenCandlesRsi'

    defaultParams: Dictionary = {
        "RSI": {
                RSI_LENGTH: rsiLength,
                RSI_BUY_THRESHOLD: rsiBuyThreshold,
                RSI_SELL_THRESHOLD: rsiSellThreshold
            },
        "NGreenCandles": {
            N_CANDLES_LENGTH: nCandlesLength,
            N_CANDLES_OPERATION: nCandlesOperation,
            N_CANDLES_OFFSET: nCandlesOffset
        },
        "Doji": {
            OPERATION_TYPE: 2
        },
        "EMADistanceCap": {
            EMA_LENGTH: 50,
            DISTANCE_PCT_CAP: 0.05
        },
        "BollingerBandWidth": {
            "bb_variation_min": 7.0
        },
        "NearSupport": {
            "support_lookback": 100,
            "tolerance_pct": 0.4,
            OPERATION_TYPE: 1
        },
        "NearEMA": {
            "ema_length": 50, 
            "tolerance_pct": 0.05,
            OPERATION_TYPE: 1
        },
        "DMNRange": {
            "dmn_min": 20.0,
            "dmn_max": 35.0,
            OPERATION_TYPE: 1
        }
    } # Inidicators parameters

    # Lists of Indicators
    baseIndicators: t.List[Indicator] = [
        # NGreenCandles("NGreenCandles", defaultParams.get("NGreenCandles", {})),
        # RSI("RSI", defaultParams.get("RSI", {}))
        DMNRange("DMNRange", defaultParams.get("DMNRange", {}))
    ] # Indicators here are mandatory conditions to generate a position

    enhancers: t.List[Indicator] = [] # Enhancers indicators can increase the position category
    weakeners: t.List[Indicator] = [] # weakeners indicators can decrease the position category
    
    # Trade Positions/Signals
    categoryAPosition: Position = Position() # This is the category with the biggest return ratio (more agressive position)
    categoryBPosition: Position # medium return reward ratio (medium agressivity)
    categoryCPosition: Position # small reward ratio (more conservative position)
    
    # Market/Data Configuration
    symbols: t.List[str] = ['BTC-USD'] # The coin pairs to which this strategy will apply
    candleInterval: str = '1d'  # Represents the data interval (e.g., 1 day)

