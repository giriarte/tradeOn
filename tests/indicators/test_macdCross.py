import unittest
from unittest.mock import patch
import pandas as pd
from indicators.constants import SIGNAL_BUY, SIGNAL_HOLD
from indicators.macdCross import MACDCross

class TestMACDCross(unittest.TestCase):

    @patch("pandas_ta.macd")
    def test_bullish_macd_cross(self, mock_macd):
        """Verify SIGNAL_BUY when MACD line crosses above Signal line."""
        # Setup: Fast=12, Slow=26, Signal=9
        macd_col = "MACD_12_26_9"
        signal_col = "MACDs_12_26_9"
        
        # Prev: MACD=1.0, Signal=1.5 (Below)
        # Curr: MACD=2.0, Signal=1.5 (Above)
        mock_output = pd.DataFrame({
            macd_col: [1.0, 2.0],
            signal_col: [1.5, 1.5]
        })
        mock_macd.return_value = mock_output
        
        data = pd.DataFrame({"Close": [100.0] * 35}) # Enough data to pass validation
        params = {'fast': 12, 'slow': 26, 'signal': 9, 'operation_type': SIGNAL_BUY}
        
        indicator = MACDCross(name="MACD_Test", params=params)
        self.assertEqual(indicator.evaluate(data), SIGNAL_BUY)