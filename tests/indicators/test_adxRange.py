import unittest
from unittest.mock import patch
import pandas as pd
from indicators.adxRange import ADXRange
from indicators.constants import SIGNAL_BUY, SIGNAL_HOLD

class TestADXRange(unittest.TestCase):

    @patch("pandas_ta.adx")
    def test_adx_within_range(self, mock_adx):
        """ADX is 30, Range is 25-40 -> Should return SIGNAL_BUY."""
        mock_adx.return_value = pd.DataFrame({"ADX_14": [30.0]})
        
        data = pd.DataFrame({"High": [10.0]*30, "Low": [9.0]*30, "Close": [9.5]*30})
        params = {'adx_min': 25.0, 'adx_max': 40.0, 'operation_type': SIGNAL_BUY}
        
        indicator = ADXRange(name="ADX_Test", params=params)
        self.assertEqual(indicator.evaluate(data), SIGNAL_BUY)

    @patch("pandas_ta.adx")
    def test_adx_too_weak(self, mock_adx):
        """ADX is 15, Min is 20 -> Should return SIGNAL_HOLD."""
        mock_adx.return_value = pd.DataFrame({"ADX_14": [15.0]})
        
        data = pd.DataFrame({"High": [10.0]*30, "Low": [9.0]*30, "Close": [9.5]*30})
        params = {'adx_min': 20.0}
        
        indicator = ADXRange(name="ADX_Test", params=params)
        self.assertEqual(indicator.evaluate(data), SIGNAL_HOLD)
