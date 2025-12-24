import unittest
from unittest.mock import patch
import pandas as pd
from indicators.constants import CLOSE_COLUMN, SIGNAL_BUY, SIGNAL_HOLD
from indicators.priceBelowBolingerBand import PriceBelowBollingerBand

class TestPriceBelowBollingerBand(unittest.TestCase):

    @patch("pandas_ta.bbands")
    def test_price_is_below_band(self, mock_bb):
        """Price 95, Lower Band 100 -> Should return SIGNAL_BUY."""
        length, std = 20, 2.0
        col_name = f"BBL_{length}_{std}_{std}"
        
        mock_bb.return_value = pd.DataFrame({col_name: [100.0]}, index=[19])
        data = pd.DataFrame({CLOSE_COLUMN: [95.0] * 20})
        
        params = {'bb_length': length, 'bb_std': std, 'operation_type': SIGNAL_BUY}
        indicator = PriceBelowBollingerBand(name="Price_Below_BB_Test", params=params)
        
        self.assertEqual(indicator.evaluate(data), SIGNAL_BUY)

    @patch("pandas_ta.bbands")
    def test_price_is_above_band_returns_hold(self, mock_bb):
        """Price 105, Lower Band 100 -> Should return SIGNAL_HOLD."""
        length, std = 20, 2.0
        col_name = f"BBL_{length}_{std}_{std}"
        
        mock_bb.return_value = pd.DataFrame({col_name: [100.0]}, index=[19])
        data = pd.DataFrame({CLOSE_COLUMN: [105.0] * 20})
        
        params = {'bb_length': length, 'bb_std': std}
        indicator = PriceBelowBollingerBand(name="Price_Below_BB_Test", params=params)
        
        self.assertEqual(indicator.evaluate(data), SIGNAL_HOLD)
