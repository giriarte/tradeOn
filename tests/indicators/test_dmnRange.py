import unittest
from unittest.mock import patch
import pandas as pd
from indicators.constants import SIGNAL_SELL, SIGNAL_HOLD
from indicators.dmnRange import DMNRange

class TestDMNRange(unittest.TestCase):

    @patch("pandas_ta.adx")
    def test_dmn_within_range(self, mock_adx):
        """DMN is 30, Range 20-40 -> Should return SIGNAL_SELL."""
        mock_adx.return_value = pd.DataFrame({"DMN_14": [30.0]})
        
        data = pd.DataFrame({"High": [10.0]*30, "Low": [9.0]*30, "Close": [9.5]*30})
        params = {'dmn_min': 20.0, 'dmn_max': 40.0, 'operation_type': SIGNAL_SELL}
        
        indicator = DMNRange(name="DMN_Test", params=params)
        self.assertEqual(indicator.evaluate(data), SIGNAL_SELL)

    @patch("pandas_ta.adx")
    def test_dmn_exceeds_max(self, mock_adx):
        """DMN is 45, Max is 40 -> Should return SIGNAL_HOLD."""
        mock_adx.return_value = pd.DataFrame({"DMN_14": [45.0]})
        
        data = pd.DataFrame({"High": [10.0]*30, "Low": [9.0]*30, "Close": [9.5]*30})
        params = {'dmn_max': 40.0}
        
        indicator = DMNRange(name="DMN_Test", params=params)
        self.assertEqual(indicator.evaluate(data), SIGNAL_HOLD)
