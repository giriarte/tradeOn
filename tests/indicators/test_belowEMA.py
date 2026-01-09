import unittest
from unittest.mock import patch
import pandas as pd
from indicators.belowEMA import BelowEMA
from indicators.constants import SIGNAL_SELL, SIGNAL_HOLD, CLOSE_COLUMN

class TestBelowEMA(unittest.TestCase):

    @patch("pandas_ta.ema")
    def test_price_is_below_ema(self, mock_ema):
        """Price 90, EMA 100 -> Should return SIGNAL_SELL."""
        mock_ema.return_value = pd.Series([100.0] * 20)
        data = pd.DataFrame({CLOSE_COLUMN: [90.0] * 20})
        
        params = {'ema_length': 20, 'operation_type': SIGNAL_SELL}
        indicator = BelowEMA(name="BelowEMA_Test", params=params)
        
        self.assertEqual(indicator.evaluate(data), SIGNAL_SELL)

    @patch("pandas_ta.ema")
    def test_price_is_above_ema_returns_hold(self, mock_ema):
        """Price 110, EMA 100 -> Should return SIGNAL_HOLD."""
        mock_ema.return_value = pd.Series([100.0] * 20)
        data = pd.DataFrame({CLOSE_COLUMN: [110.0] * 20})
        
        params = {'ema_length': 20}
        indicator = BelowEMA(name="BelowEMA_Test", params=params)
        
        self.assertEqual(indicator.evaluate(data), SIGNAL_HOLD)
