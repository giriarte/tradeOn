import unittest
from unittest.mock import patch
import pandas as pd
from indicators.constants import SIGNAL_BUY, SIGNAL_HOLD
from indicators.stochasticRSICross import StochasticRSICross

class TestStochasticRSICross(unittest.TestCase):

    @patch("pandas_ta.stochrsi")
    def test_stoch_rsi_bullish_cross_with_threshold(self, mock_stoch):
        """K crosses D at level 15 (below threshold 20) -> Should return SIGNAL_BUY."""
        k_col = "STOCHRSIk_14_14_3_3"
        d_col = "STOCHRSId_14_14_3_3"
        
        # Previous: K=10, D=12 | Current: K=15, D=13 (Crossed Above)
        mock_stoch.return_value = pd.DataFrame({
            k_col: [10.0, 15.0],
            d_col: [12.0, 13.0]
        })
        
        data = pd.DataFrame({"Close": [100.0] * 40})
        params = {
            'threshold': 20.0, 
            'operation_type': SIGNAL_BUY
        }
        
        indicator = StochasticRSICross(name="StochCross_Test", params=params)
        self.assertEqual(indicator.evaluate(data), SIGNAL_BUY)

    @patch("pandas_ta.stochrsi")
    def test_stoch_rsi_cross_ignored_above_threshold(self, mock_stoch):
        """K crosses D at level 50 (above threshold 20) -> Should return SIGNAL_HOLD."""
        k_col = "STOCHRSIk_14_14_3_3"
        d_col = "STOCHRSId_14_14_3_3"
        
        # Crossed at level 50
        mock_stoch.return_value = pd.DataFrame({
            k_col: [48.0, 52.0],
            d_col: [50.0, 50.0]
        })
        
        data = pd.DataFrame({"Close": [100.0] * 40})
        params = {'threshold': 20.0, 'operation_type': SIGNAL_BUY}
        
        indicator = StochasticRSICross(name="StochCross_Test", params=params)
        self.assertEqual(indicator.evaluate(data), SIGNAL_HOLD)
