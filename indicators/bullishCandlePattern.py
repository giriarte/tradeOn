import typing as t
from indicators.InvertedHammer import InvertedHammer
from indicators.constants import SIGNAL_BUY, SIGNAL_HOLD
from indicators.dragonFlyDoji import DragonflyDoji
from indicators.engulfing import Engulfing
from indicators.hammer import Hammer
from indicators.harami import Harami
from indicators.morningStar import MorningStar
from .indicator import Indicator


class BullishCandlePattern(Indicator):
    """
    A composite indicator that aggregates multiple bullish candlestick patterns.
    It returns SIGNAL_BUY if any of the underlying indicators detect a pattern.
    """

    def __init__(self, name: str, params: t.Dict[str, t.Any] = None):
        super().__init__(name, params)
        # Initialize the subset of bullish indicators
        self.bullish_indicators = [
            Engulfing("Engulfing", params),
            Harami("Harami", params),
            DragonflyDoji("DragonflyDoji", params),
            Hammer("Hammer", params),
            InvertedHammer("InvertedHammer", params),
            MorningStar("MorningStar", params)
        ]

    def evaluate(self, df: t.Any, params: t.Optional[t.Dict[str, t.Any]] = None) -> int:
        """
        Iterates through all registered bullish indicators. 
        Returns SIGNAL_BUY at the first match found.
        """
        # Use instance parameters if none are provided
        if params is None:
            params = self.params

        for indicator in self.bullish_indicators:
            # We call evaluate on each sub-indicator
            signal = indicator.evaluate(df, params)
            
            if signal == SIGNAL_BUY:
                # Log which specific pattern triggered the buy
                print(f"Composite Bullish Signal triggered by: {indicator.__class__.__name__}")
                return SIGNAL_BUY

        return SIGNAL_HOLD