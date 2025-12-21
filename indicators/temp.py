import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Strategies')

strategy_item = {
    "userId": "12345",                    # Partition Key
    "strategyId": "strat-998877",         # Useful if you have multiple strategies per user
    "name": "Bullish Momentum Alpha",
    
    # Stored as a list of strings (to be hydrated into objects by the Lambda)
    "baseIndicators": ["NGreenCandles", "RSI"], 
    
    # Map structure for the Position object
    "categoryAPosition": {
        "type": 1,
        "cost": Decimal('1000.0'),
        "stopLoss": Decimal('0.05'),                 # 5% 
        "takeProfit": Decimal('0.15'),                # 15%
        "trailingStopIncreaseRatio": Decimal('0.02'),
        "action": "BUY",
        "leverage": Decimal('5.0'),
        "asset": "USDT"
    },
    
    "brokerId": "BINANCE_001",
    "symbols": ["BTC/USDT", "ETH/USDT", "SOL/USDT"],
    "candleInterval": "1h",
    
    # Parameters used by the indicator implementations
    "defaultParams": {
        "NGreenCandles": {"n_period": 3},
        "RSI": {"period": 14, "overbought": 70, "oversold": 30}
    }
}

table.put_item(Item=strategy_item)

