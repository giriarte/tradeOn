import unittest
from unittest.mock import patch
import pandas as pd
from indicators.constants import EMA_LENGTH, OPERATION_TYPE, SIGNAL_BUY, SIGNAL_HOLD, CLOSE_COLUMN, TOLERANCE_PCT
from indicators.nearEma import NearEMA

class TestNearEMA(unittest.TestCase):

    @patch("pandas_ta.ema")
    def test_price_is_near_ema(self, mock_ema):
        """EMA is 100, Price is 100.2 (0.2% dist), Tolerance 0.5% -> Trigger."""
        # Setup mock to return 100 as the current EMA value
        mock_ema.return_value = pd.Series([100.0] * 20)
        
        data = pd.DataFrame({CLOSE_COLUMN: [100.2] * 20})
        params = {
            EMA_LENGTH: 20, 
            TOLERANCE_PCT: 0.5, 
            OPERATION_TYPE: SIGNAL_BUY
        }
        
        indicator = NearEMA(name="NearEMA_Test", params=params)
        self.assertEqual(indicator.evaluate(data), SIGNAL_BUY)

    @patch("pandas_ta.ema")
    def test_price_is_too_far_from_ema(self, mock_ema):
        """EMA is 100, Price is 102.0 (2.0% dist), Tolerance 0.5% -> HOLD."""
        mock_ema.return_value = pd.Series([100.0] * 20)
        
        data = pd.DataFrame({CLOSE_COLUMN: [102.0] * 20})
        params = {EMA_LENGTH: 20, TOLERANCE_PCT: 0.5}
        
        indicator = NearEMA(name="NearEMA_Test", params=params)
        self.assertEqual(indicator.evaluate(data), SIGNAL_HOLD)
