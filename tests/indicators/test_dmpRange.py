import unittest
from unittest.mock import patch
import pandas as pd
from indicators.constants import SIGNAL_BUY, SIGNAL_HOLD
from indicators.dmpRange import DMPRange

class TestDMPRange(unittest.TestCase):

    @patch("pandas_ta.adx")
    def test_dmp_within_range(self, mock_adx):
        """DMP is 28, Range is 20-35 -> Should return SIGNAL_BUY."""
        # Note: pandas_ta.adx returns DMP_{length}
        mock_adx.return_value = pd.DataFrame({"DMP_14": [28.0]})
        
        data = pd.DataFrame({"High": [10.0]*30, "Low": [9.0]*30, "Close": [9.5]*30})
        params = {'dmp_min': 20.0, 'dmp_max': 35.0, 'operation_type': SIGNAL_BUY}
        
        indicator = DMPRange(name="DMP_Test", params=params)
        self.assertEqual(indicator.evaluate(data), SIGNAL_BUY)

    @patch("pandas_ta.adx")
    def test_dmp_below_min(self, mock_adx):
        """DMP is 15, Min is 20 -> Should return SIGNAL_HOLD."""
        mock_adx.return_value = pd.DataFrame({"DMP_14": [15.0]})
        
        data = pd.DataFrame({"High": [10.0]*30, "Low": [9.0]*30, "Close": [9.5]*30})
        params = {'dmp_min': 20.0}
        
        indicator = DMPRange(name="DMP_Test", params=params)
        self.assertEqual(indicator.evaluate(data), SIGNAL_HOLD)
