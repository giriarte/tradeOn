from indicators.indicatorRegistry import get_indicator_instance
from strategies.position import Position
from strategies.strategy import TradeStrategy


def create_strategy(item: dict) -> TradeStrategy:
    # 1. Create the Position object
    pos_data = item.get('categoryAPosition', {})
    category_a = Position(
        # type=int(pos_data.get('type', 0)),
        # cost=float(pos_data.get('cost', 0.0)),
        # stopLoss=float(pos_data.get('stopLoss', 0.0)),
        # takeProfit=float(pos_data.get('takeProfit', 0.0)),
        # trailingStopIncreaseRatio=pos_data.get('trailingStopIncreaseRatio'),
        # action=pos_data.get('action', ''),
        # leverage=float(pos_data.get('leverage', 1.0)),
        # asset=pos_data.get('asset', '')
    )

    # 2. Convert Indicator names to Concrete Objects
    indicator_names = item.get('baseIndicators', [])
    base_indicators = [get_indicator_instance(name, item.get('defaultParams', {})) for name in indicator_names]

    # 3. Build the TradeStrategy
    return TradeStrategy(
        name=item.get('name'),
        baseIndicators=base_indicators,
        categoryAPosition=category_a,
        brokerId=item.get('brokerId'),
        symbols=item.get('symbols', []),
        candleInterval=item.get('candleInterval'),
        defaultParams=item.get('defaultParams', {})
    )