import unittest
import pandas as pd
from indicators.constants import OPERATION_TYPE, RESISTANCE_LOOKBACK, SIGNAL_SELL, SIGNAL_HOLD, CLOSE_COLUMN, HIGH_COLUMN, TOLERANCE_PCT
from indicators.nearResistance import NearResistance

class TestNearResistance(unittest.TestCase):

    def test_identifies_local_high_and_triggers(self):
        """
        Should find 120.0 as the high in a 3-candle lookback.
        Current price 119.5 is within 0.5% tolerance of 120.0.
        """
        data = pd.DataFrame({
            HIGH_COLUMN:  [110.0, 120.0, 115.0, 119.5], # Resistance is 120.0 (Index -3)
            CLOSE_COLUMN: [108.0, 118.0, 114.0, 119.5]  # Current is 119.5
        })
        
        params = {
            RESISTANCE_LOOKBACK: 3, 
            TOLERANCE_PCT: 0.5, 
            OPERATION_TYPE: SIGNAL_SELL
        }
        
        indicator = NearResistance(name="NearResistance_Test", params=params)
        self.assertEqual(indicator.evaluate(data), SIGNAL_SELL)

    def test_outside_tolerance_returns_hold(self):
        """Resistance 120.0, Price 110.0 -> Should return HOLD."""
        data = pd.DataFrame({
            HIGH_COLUMN:  [120.0, 115.0, 110.0], # Resistance is 120.0
            CLOSE_COLUMN: [118.0, 114.0, 110.0]  # Current is 110.0 (too far)
        })
        
        params = {'resistance_lookback': 2, 'tolerance_pct': 1.0}
        indicator = NearResistance(name="NearResistance_Test", params=params)
        
        self.assertEqual(indicator.evaluate(data), SIGNAL_HOLD)
