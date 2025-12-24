import unittest
import pandas as pd
from indicators.constants import SIGNAL_BUY, CLOSE_COLUMN, LOW_COLUMN
from indicators.nearSupport import NearSupport

class TestNearSupport(unittest.TestCase):

    def test_identifies_local_low_and_triggers(self):
        """
        Should find 100.0 as the low in a 3-candle lookback.
        Current price 100.2 is within 0.5% tolerance of 100.0.
        """
        data = pd.DataFrame({
            LOW_COLUMN:   [110.0, 100.0, 105.0, 100.2], # Index -2 is 105.0, Index -3 is 100.0
            CLOSE_COLUMN: [112.0, 101.0, 106.0, 100.2]  # Current price is 100.2
        })
        
        params = {
            'support_lookback': 3, 
            'tolerance_pct': 0.5, 
            'operation_type': SIGNAL_BUY
        }
        
        indicator = NearSupport(name="NearSupport_Test", params=params)
        self.assertEqual(indicator.evaluate(data), SIGNAL_BUY)

    def test_ignores_current_low_for_support_calculation(self):
        """
        The lookback should only consider historical lows.
        Even if current low is 90, if previous low was 100, 
        current price 100.1 should trigger based on 100.
        """
        data = pd.DataFrame({
            LOW_COLUMN:   [100.0, 110.0, 90.0], # Support should be 100.0 (historical)
            CLOSE_COLUMN: [102.0, 111.0, 100.1] # Current price 100.1 is near 100.0
        })
        
        params = {'support_lookback': 2, 'tolerance_pct': 0.5}
        indicator = NearSupport(name="NearSupport_Test", params=params)
        
        self.assertEqual(indicator.evaluate(data), SIGNAL_BUY)
