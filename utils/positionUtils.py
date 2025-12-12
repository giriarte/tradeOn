def getTradeSize(cost, closeValue, leverage):
    """
    Calculates the maximum trade size (number of units) for a position.

    :param cost: The total capital available for the trade (e.g., 1000).
    :param closeValue: The price of the asset per unit (e.g., 50.00).
    :param leverage: The leverage ratio being used (e.g., 10 for 10:1).
    :return: The calculated trade size as an integer (number of units).
    """

    # 1. Calculate the maximum total value of the position (Cost * Leverage)
    max_position_value = cost * leverage

    # 2. Calculate the raw number of units by dividing the max value by the unit price
    raw_size = max_position_value / closeValue

    trade_size = round(raw_size, 0) 
    
    return trade_size