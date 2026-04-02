from indicators.indicatorRegistry import get_indicator_instance
from strategies.position import Position
from model.strategy import TradeStrategy


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

    # Convert Indicator names to Concrete Objects
    # Access the raw list from the DynamoDB item (now a list of dicts/maps)
    # Structure expected: [{'name': 'EMACross', 'offset': 5}, {'name': 'ADXRange'}]
    raw_indicator_data = item.get('baseIndicators', [])
    base_indicators = [get_indicator_instance(entry.get('name'), entry.get('params', {}), entry.get('offset')) for entry in raw_indicator_data]

    # 3. Build the TradeStrategy
    return TradeStrategy(
        name=item.get('name'),
        baseIndicators=base_indicators,
        categoryAPosition=category_a,
        brokerId=item.get('brokerId'),
        symbols=item.get('symbols', []),
        candleInterval=item.get('candleInterval'),
        strategyId=item.get('strategyId'),
        userId=item.get('userId'),
        cooldownInterval=int(item['cooldownInterval']) if item.get('cooldownInterval') is not None else None,
    )