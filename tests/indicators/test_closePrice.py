import unittest
import pandas as pd
from indicators.closePrice import ClosePrice
from indicators.constants import SIGNAL_BUY, SIGNAL_HOLD, CLOSE_COLUMN

class TestClosePrice(unittest.TestCase):

    def test_price_within_range_above(self):
        """Price is 100.4, Level is 100.0 (0.4% dist), Tolerance 0.5% -> BUY."""
        data = pd.DataFrame({CLOSE_COLUMN: [100.4]})
        params = {'target_level': 100.0, 'tolerance_pct': 0.5, 'operation_type': SIGNAL_BUY}
        
        indicator = ClosePrice(name="ClosePrice_Test", params=params)
        self.assertEqual(indicator.evaluate(data), SIGNAL_BUY)

    def test_price_within_range_below(self):
        """Price is 99.6, Level is 100.0 (0.4% dist), Tolerance 0.5% -> BUY."""
        data = pd.DataFrame({CLOSE_COLUMN: [99.6]})
        params = {'target_level': 100.0, 'tolerance_pct': 0.5}
        
        indicator = ClosePrice(name="Support_Test", params=params)
        self.assertEqual(indicator.evaluate(data), SIGNAL_BUY)

    def test_price_outside_range(self):
        """Price is 101.0, Level is 100.0 (1.0% dist), Tolerance 0.5% -> HOLD."""
        data = pd.DataFrame({CLOSE_COLUMN: [101.0]})
        params = {'target_level': 100.0, 'tolerance_pct': 0.5}
        
        indicator = ClosePrice(name="Support_Test", params=params)
        self.assertEqual(indicator.evaluate(data), SIGNAL_HOLD)
