import unittest
from unittest.mock import patch
import pandas as pd
from indicators.constants import SIGNAL_SELL, SIGNAL_HOLD
from indicators.priceAboveBollingerBand import PriceAboveBollingerBand

class TestPriceAboveBollingerBand(unittest.TestCase):

    @patch("pandas_ta.bbands")
    def test_price_is_above_band(self, mock_bb):
        """Price 105, Upper Band 100 -> Should return SIGNAL_SELL."""
        length, std = 20, 2.0
        col_name = f"BBU_{length}_{std}_{std}"
        
        mock_bb.return_value = pd.DataFrame({col_name: [100.0]}, index=[19])
        data = pd.DataFrame({"Close": [105.0] * 20})
        
        params = {'bb_length': length, 'bb_std': std, 'operation_type': SIGNAL_SELL}
        indicator = PriceAboveBollingerBand(name="Price_Above_BB_Test", params=params)
        
        self.assertEqual(indicator.evaluate(data), SIGNAL_SELL)

    @patch("pandas_ta.bbands")
    def test_price_is_below_upper_returns_hold(self, mock_bb):
        """Price 95, Upper Band 100 -> Should return SIGNAL_HOLD."""
        length, std = 20, 2.0
        col_name = f"BBU_{length}_{std}_{std}"
        
        mock_bb.return_value = pd.DataFrame({col_name: [100.0]}, index=[19])
        data = pd.DataFrame({"Close": [95.0] * 20})
        
        params = {'bb_length': length, 'bb_std': std}
        indicator = PriceAboveBollingerBand(name="Price_Above_BB_Test", params=params)
        
        self.assertEqual(indicator.evaluate(data), SIGNAL_HOLD)
