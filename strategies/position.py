
class Position:
    type: int
    cost: float
    stopLoss: float
    takeProfit: float
    # exitStrategy: Strategy | None TODO: This is a circular dependency. Figure out how to fix it
    trailingStopIncreaseRatio: float | None
    action: str = ''
    leverage: float
    asset: str
