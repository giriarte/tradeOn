import unittest
from unittest.mock import patch
import pandas as pd
from indicators.constants import SIGNAL_BUY, SIGNAL_HOLD
from indicators.emaDistanceCap import EMADistanceCap

class TestEMADistanceCap(unittest.TestCase):
    
    @patch("pandas_ta.ema")
    def test_evaluate_within_cap(self, mock_ema):
        """Price is 0.5% above EMA, cap is 1.0% -> Should BUY."""
        mock_ema.return_value = pd.Series([100.0] * 20)
        data = pd.DataFrame({"Close": [100.0] * 19 + [100.5]})
        
        params = {'ema_length': 20, 'distance_pct_cap': 1.0, 'operation_type': SIGNAL_BUY}
        indicator = EMADistanceCap(name="EMA_Cap", params=params)
        
        self.assertEqual(indicator.evaluate(data), SIGNAL_BUY)

    @patch("pandas_ta.ema")
    def test_evaluate_exceeds_cap(self, mock_ema):
        """Price is 2.0% above EMA, cap is 1.0% -> Should HOLD (too far)."""
        mock_ema.return_value = pd.Series([100.0] * 20)
        data = pd.DataFrame({"Close": [100.0] * 19 + [102.0]})
        
        params = {'ema_length': 20, 'distance_pct_cap': 1.0, 'operation_type': SIGNAL_BUY}
        indicator = EMADistanceCap(name="EMA_Cap", params=params)
        
        self.assertEqual(indicator.evaluate(data), SIGNAL_HOLD)
