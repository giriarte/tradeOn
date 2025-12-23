import unittest
from unittest.mock import patch
import pandas as pd
from indicators.constants import SIGNAL_BUY, SIGNAL_HOLD
from indicators.emaCross import EMACross

class TestEMACross(unittest.TestCase):

    @patch("pandas_ta.ema")
    def test_evaluate_detects_bullish_cross_2_4(self, mock_ema):
        """Verify SIGNAL_BUY when Fast EMA (2) crosses above Slow EMA (4)."""
        # Setup: Fast EMA (2) and Slow EMA (4)
        # Prev (-2): Fast=10.0, Slow=12.0 (Fast is BELOW Slow)
        # Curr (-1): Fast=13.0, Slow=12.5 (Fast is ABOVE Slow)
        def side_effect(series, length):
            if length == 2: 
                return pd.Series([10.0, 13.0])
            if length == 4: 
                return pd.Series([12.0, 12.5])
            return None

        mock_ema.side_effect = side_effect
        
        # We need at least length of high_period + 1 rows in the DF (4 + 1 = 5)
        # However, because we are mocking the output directly, 2 rows are enough 
        # for the iloc[-1] and iloc[-2] calls to work on the mock series.
        df = pd.DataFrame({"Close": [10.0, 11.0, 12.0, 13.0, 14.0]})
        
        params = {
            'ema_low': 2, 
            'ema_high': 4, 
            'operation_type': SIGNAL_BUY
        }
        indicator = EMACross(name="Cross_2_4_Test", params=params)
        
        # Act
        signal = indicator.evaluate(df, params=params)
        
        # Assert
        self.assertEqual(signal, SIGNAL_BUY)

    @patch("pandas_ta.ema")
    def test_evaluate_no_signal_if_already_above(self, mock_ema):
        """Verify SIGNAL_HOLD if Fast is already above Slow (no cross occurred)."""
        def side_effect(series, length):
            if length == 9: return pd.Series([105.0, 110.0])
            if length == 21: return pd.Series([100.0, 100.0])
            return None

        mock_ema.side_effect = side_effect
        df = pd.DataFrame({"Close": [100.0, 101.0]})
        
        params = {'ema_low': 9, 'ema_high': 21, 'operation_type': SIGNAL_BUY}
        indicator = EMACross(name="Cross_Test", params=params)
        
        self.assertEqual(indicator.evaluate(df), SIGNAL_HOLD)
