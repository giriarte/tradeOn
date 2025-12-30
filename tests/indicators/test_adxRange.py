import unittest
from unittest.mock import patch
import pandas as pd
from indicators.adxRange import ADXRange
from indicators.constants import ADX_MAX, ADX_MIN, CLOSE_COLUMN, HIGH_COLUMN, LOW_COLUMN, OPERATION_TYPE, SIGNAL_BUY, SIGNAL_HOLD

class TestADXRange(unittest.TestCase):

    @patch("pandas_ta.adx")
    def test_adx_within_range(self, mock_adx):
        """ADX is 30, Range is 25-40 -> Should return SIGNAL_BUY."""
        mock_adx.return_value = pd.DataFrame({"ADX_14": [30.0]})
        
        data = pd.DataFrame({HIGH_COLUMN: [10.0]*30, LOW_COLUMN: [9.0]*30, CLOSE_COLUMN: [9.5]*30})
        params = {ADX_MIN: 25.0, ADX_MAX: 40.0, OPERATION_TYPE: SIGNAL_BUY}
        
        indicator = ADXRange(name="ADX_Test", params=params)
        self.assertEqual(indicator.evaluate(data), SIGNAL_BUY)

    @patch("pandas_ta.adx")
    def test_adx_too_weak(self, mock_adx):
        """ADX is 15, Min is 20 -> Should return SIGNAL_HOLD."""
        mock_adx.return_value = pd.DataFrame({"ADX_14": [15.0]})
        
        data = pd.DataFrame({HIGH_COLUMN: [10.0]*30, LOW_COLUMN: [9.0]*30, CLOSE_COLUMN: [9.5]*30})
        params = {ADX_MIN: 20.0}
        
        indicator = ADXRange(name="ADX_Test", params=params)
        self.assertEqual(indicator.evaluate(data), SIGNAL_HOLD)
