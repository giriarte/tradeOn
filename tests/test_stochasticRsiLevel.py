import unittest
from unittest.mock import patch
import pandas as pd
from indicators.constants import SIGNAL_BUY, SIGNAL_SELL, SIGNAL_HOLD
from indicators.stochasticRSILevel import StochasticRSILevel

class TestStochasticRSILevel(unittest.TestCase):

    @patch("pandas_ta.stochrsi")
    def test_stoch_rsi_oversold_buy(self, mock_stoch):
        """K is 15.0, Threshold 20.0 -> Should return SIGNAL_BUY."""
        k_col = "STOCHRSIk_14_14_3_3"
        mock_stoch.return_value = pd.DataFrame({k_col: [15.0]})
        
        data = pd.DataFrame({"Close": [100.0] * 40})
        params = {'threshold': 20.0, 'operation_type': SIGNAL_BUY}
        
        indicator = StochasticRSILevel(name="Stoch_Test", params=params)
        self.assertEqual(indicator.evaluate(data), SIGNAL_BUY)

    @patch("pandas_ta.stochrsi")
    def test_stoch_rsi_overbought_sell(self, mock_stoch):
        """K is 85.0, Threshold 80.0 -> Should return SIGNAL_SELL."""
        k_col = "STOCHRSIk_14_14_3_3"
        mock_stoch.return_value = pd.DataFrame({k_col: [85.0]})
        
        data = pd.DataFrame({"Close": [100.0] * 40})
        params = {'threshold': 80.0, 'operation_type': SIGNAL_SELL}
        
        indicator = StochasticRSILevel(name="Stoch_Test", params=params)
        self.assertEqual(indicator.evaluate(data), SIGNAL_SELL)
