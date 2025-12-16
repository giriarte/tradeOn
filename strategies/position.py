
from indicators.indicator import Indicator
import typing as t


class Position:
    type: int
    cost: float
    stopLoss: float
    takeProfit: float
    exitSignal: t.List[Indicator] | None
    trailingStopIncreaseRatio: float | None
    action: str = ''
    leverage: float
    asset: str
