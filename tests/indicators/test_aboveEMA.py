import unittest
from unittest.mock import patch
import pandas as pd
from indicators.aboveEMA import AboveEMA
from indicators.constants import SIGNAL_BUY, SIGNAL_HOLD, CLOSE_COLUMN

class TestAboveEMA(unittest.TestCase):

    @patch("pandas_ta.ema")
    def test_price_is_above_ema(self, mock_ema):
        """Price 110, EMA 100 -> Should return SIGNAL_BUY."""
        mock_ema.return_value = pd.Series([100.0] * 20)
        data = pd.DataFrame({CLOSE_COLUMN: [110.0] * 20})
        
        params = {'ema_length': 20, 'operation_type': SIGNAL_BUY}
        indicator = AboveEMA(name="AboveEMA_Test", params=params)
        
        self.assertEqual(indicator.evaluate(data), SIGNAL_BUY)

    @patch("pandas_ta.ema")
    def test_price_is_below_ema_returns_hold(self, mock_ema):
        """Price 90, EMA 100 -> Should return SIGNAL_HOLD."""
        mock_ema.return_value = pd.Series([100.0] * 20)
        data = pd.DataFrame({CLOSE_COLUMN: [90.0] * 20})
        
        params = {'ema_length': 20}
        indicator = AboveEMA(name="AboveEMA_Test", params=params)
        
        self.assertEqual(indicator.evaluate(data), SIGNAL_HOLD)
