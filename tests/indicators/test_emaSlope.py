import unittest
from unittest.mock import patch
import pandas as pd
from indicators.constants import SIGNAL_BUY, SIGNAL_HOLD
from indicators.emaSlope import EMASlope

class TestEMASlope(unittest.TestCase):

    @patch("pandas_ta.ema")
    def test_steep_negative_slope_returns_signal(self, mock_ema):
        """EMA falling from 100 to 95 is a -5% slope. Modulus is 5%, which should trigger."""
        # Previous EMA = 100, Current EMA = 95
        mock_ema.return_value = pd.Series([100.0] * 10 + [100.0, 95.0])
        df = pd.DataFrame({"Close": [100.0] * 12})
        
        # We set threshold at 4%
        params = {'ema_length': 10, 'lookback': 1, 'min_slope_pct': 4.0}
        indicator = EMASlope(name="Slope_Modulus_Test", params=params)
        
        # Even though it's falling, the absolute slope is 5% >= 4%
        self.assertEqual(indicator.evaluate(df), SIGNAL_BUY)

    @patch("pandas_ta.ema")
    def test_flat_slope_below_threshold_returns_hold(self, mock_ema):
        """EMA rising from 100 to 100.1 is 0.1%. Threshold 0.5% -> HOLD."""
        mock_ema.return_value = pd.Series([100.0] * 10 + [100.0, 100.1])
        df = pd.DataFrame({"Close": [100.0] * 12})
        
        params = {'ema_length': 10, 'lookback': 1, 'min_slope_pct': 0.5}
        indicator = EMASlope(name="Slope_Modulus_Test", params=params)
        
        self.assertEqual(indicator.evaluate(df), SIGNAL_HOLD)