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
from indicators.constants import (
    DISTANCE_PCT_CAP,
    EMA_LENGTH,
    MIN_RAW_SLOPE_PCT,
    N_CANDLES_LENGTH,
    N_CANDLES_OFFSET,
    N_CANDLES_OPERATION,
    OPERATION_TYPE, 
    RSI_BUY_THRESHOLD, 
    RSI_LENGTH, 
    RSI_SELL_THRESHOLD
)
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
from model.strategy import TradeStrategy, Position

Dictionary = t.Dict[str, t.Dict[str, t.Any]] # Represents the default parameters map

class ThreeGreenCandlesRsi(TradeStrategy):
    nCandlesLength = 3
    nCandlesOperation = 2
    nCandlesOffset = 0

    # --- ATTRIBUTES (Class Variables or Properties for definition) ---
    name: str = 'ThreeGreenCandlesRsi'

    defaultParams: Dictionary = {
        "RSI": {
            RSI_LENGTH: 16,
            RSI_BUY_THRESHOLD: 45,
            RSI_SELL_THRESHOLD: 55,
            OPERATION_TYPE: 1,
        },
        "NRedCandles": {    
            N_CANDLES_LENGTH: 1,
            N_CANDLES_OPERATION: 2,
            N_CANDLES_OFFSET: 0
        },
        "NGreenCandles": {
            N_CANDLES_LENGTH: 1,
            N_CANDLES_OPERATION: 1,
            N_CANDLES_OFFSET: 0
        },
        "StochasticRSICross": {
            OPERATION_TYPE: 1,
            "threshold": 20
        },
        "NearEMA": {
            EMA_LENGTH: 50,
            DISTANCE_PCT_CAP: 0.05,
            OPERATION_TYPE: 1
        },
        "MACDDivergence": {
            "bb_variation_min": 4.0,
            OPERATION_TYPE: 2
        },
        "NearSupport": {
            "support_lookback": 100,
            "tolerance_pct": 0.4,
            OPERATION_TYPE: 1
        },
        "BelowEMA": {
            "ema_length": 200, 
            OPERATION_TYPE: 2
        },
        "DMNRange": {
            "dmn_min": 0.01,
            OPERATION_TYPE: 2
        },
        "DMPRange": {
            "dmp_max": 0.01,
            OPERATION_TYPE: 2
        },
        "BollingerBandReEntry": {
            OPERATION_TYPE: 1,
            'bb_length': 26
        },
        "EMASlope": {
            OPERATION_TYPE: 1,
            "lookback": 20,
            "ema_length":50,
            MIN_RAW_SLOPE_PCT: 0.1
        },
        "AboveEMA": {
            "ema_length": 200,
            OPERATION_TYPE: 1
        },
        "BearishCandlePattern": {
            OPERATION_TYPE: 2
        },
        "ADXRange": {
            "adx_min": 25,
            OPERATION_TYPE: 1
        },
        "MACDCross": {
            OPERATION_TYPE: 1
        },
        "EMACross": {
            OPERATION_TYPE: 2,
            "ema_low": 21,
            "ema_high": 55
        },
        "CustomCandle": { # Customizing as a bearish hammer
            OPERATION_TYPE: 1,
            "upper_wick_min": 0,
            "upper_wick_max": 20, # 10 for automated, 20 for manual verification
            "lower_wick_min": 50, # 50 for automated, 35 for manual verification
            "lower_wick_max": 100
        },
        "LongCandle": {
            OPERATION_TYPE: 1,
            "multiplier": 1.5,
        }
    } # Inidicators parameters

    # Lists of Indicators
    baseIndicators: t.List[Indicator] = [
        CustomCandle("CustomCandle", defaultParams.get("CustomCandle", {})), # Customizing as a bullish hammer this time.
        LongCandle("LongCandle", defaultParams.get("LongCandle", {}), 0),
        RSI("RSI", defaultParams.get("RSI", {}), 1),
        NGreenCandles("NGreenCandles", defaultParams.get("NGreenCandles", {}), 0),
        #NRedCandles("NRedCandles", defaultParams.get("NRedCandles", {}), 0),
        # PriceBelowBollingerBand("PriceBelowBollingerBand", defaultParams.get("PriceBelowBollingerBand", {}), 1),
        # BollingerBandReEntry("BollingerBandReEntry", defaultParams.get("BollingerBandReEntry", {}), 0),
        #BearishCandlePattern("BearishCandlePattern", defaultParams.get("BearishCandlePattern", {}), 0)
        # EMASlope("EMASlope", defaultParams.get("EMASlope", {}), 1)
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

