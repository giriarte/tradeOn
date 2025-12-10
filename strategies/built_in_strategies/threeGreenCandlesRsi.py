import typing as t
from indicators.constants import (
    N_CANDLES_LENGTH,
    N_CANDLES_OFFSET,
    N_CANDLES_OPERATION, 
    RSI_BUY_THRESHOLD, 
    RSI_LENGTH, 
    RSI_SELL_THRESHOLD
)
from indicators.indicator import Indicator
from indicators.nGreenCandles import NGreenCandles
from indicators.rsi import RSI
from strategies.strategy import TradeStrategy, Position

Dictionary = t.Dict[str, t.Dict[str, t.Any]] # Represents the default parameters map

class ThreeGreenCandlesRsi(TradeStrategy):
    # --- ATTRIBUTES (Class Variables or Properties for definition) ---
    name: str = 'ThreeGreenCandlesRsi'

    # Lists of Indicators
    baseIndicators: t.List[Indicator] = [
        NGreenCandles(),
        RSI()
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
    defaultParams: Dictionary = {
        RSI_LENGTH: 10,
        RSI_BUY_THRESHOLD: 30,
        RSI_SELL_THRESHOLD: 70,
        N_CANDLES_LENGTH: 3,
        N_CANDLES_OPERATION: 2,
        N_CANDLES_OFFSET: 1
    } # Inidicators parameters