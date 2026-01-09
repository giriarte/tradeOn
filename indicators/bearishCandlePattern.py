import typing as t
from indicators.constants import SIGNAL_SELL, SIGNAL_HOLD
from indicators.engulfing import Engulfing
from indicators.eveningStar import EveningStar
from indicators.gravestoneDoji import GravestoneDoji
from indicators.hangingMan import HangingMan
from indicators.harami import Harami
from indicators.shootingStar import ShootingStar
from .indicator import Indicator


class BearishCandlePattern(Indicator):
    """
    A composite indicator that aggregates multiple bearish candlestick patterns.
    It returns SIGNAL_SELL if any of the underlying indicators detect a pattern.
    """

    def __init__(self, name: str, params: t.Dict[str, t.Any] = None, offset: int = None):
        super().__init__(name, params, offset)
        # Initialize the subset of bearish indicators
        self.bearish_indicators = [
            Engulfing("Engulfing", params),
            Harami("Harami", params),
            GravestoneDoji("GravestoneDoji", params),
            ShootingStar("ShootingStar", params),
            HangingMan("HangingMan", params),
            EveningStar("EveningStar", params)
        ]

    def evaluate(self, df: t.Any, params: t.Optional[t.Dict[str, t.Any]] = None) -> int:
        """
        Iterates through all registered bearish indicators. 
        Returns SIGNAL_SELL at the first match found.
        """
        if params is None:
            params = self.params

        for indicator in self.bearish_indicators:
            # Call evaluate on each sub-indicator
            signal = indicator.evaluate(df, params)
            
            if signal == SIGNAL_SELL:
                # Log which specific pattern triggered the sell
                print(f"Composite Bearish Signal triggered by: {indicator.__class__.__name__}")
                return SIGNAL_SELL

        return SIGNAL_HOLD