import typing as t
from indicators.InvertedHammer import InvertedHammer
from indicators.bearishCandlePattern import BearishCandlePattern
from indicators.bullishCandlePattern import BullishCandlePattern
from indicators.constants import (
    N_CANDLES_LENGTH,
    N_CANDLES_OFFSET,
    N_CANDLES_OPERATION,
    OPERATION_TYPE, 
    RSI_BUY_THRESHOLD, 
    RSI_LENGTH, 
    RSI_SELL_THRESHOLD
)
from indicators.doji import Doji
from indicators.dragonFlyDoji import DragonflyDoji
from indicators.engulfing import Engulfing
from indicators.eveningStar import EveningStar
from indicators.gravestoneDoji import GravestoneDoji
from indicators.hammer import Hammer
from indicators.hangingMan import HangingMan
from indicators.harami import Harami
from indicators.indicator import Indicator
from indicators.morningStar import MorningStar
from indicators.nGreenCandles import NGreenCandles
from indicators.rsi import RSI
from indicators.shootingStar import ShootingStar
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
        }
    } # Inidicators parameters

    # Lists of Indicators
    baseIndicators: t.List[Indicator] = [
        # NGreenCandles("NGreenCandles", defaultParams.get("NGreenCandles", {})),
        # RSI("RSI", defaultParams.get("RSI", {}))
        BearishCandlePattern("BearishCandlePattern", defaultParams.get("BearishCandlePattern", {}))
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

