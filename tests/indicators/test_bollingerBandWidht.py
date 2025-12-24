import unittest
from unittest.mock import patch
import pandas as pd
from indicators.bollingerBandWidth import BollingerBandWidth
from indicators.constants import SIGNAL_BUY, SIGNAL_HOLD

class TestBollingerBandWidth(unittest.TestCase):

    @patch("pandas_ta.bbands")
    def test_bandwidth_within_range(self, mock_bb):
        """Bandwidth is 5.0, range is 2.0 - 10.0 -> Should trigger."""
        mock_output = pd.DataFrame({"BBB_20_2.0_2.0": [5.0]})
        mock_bb.return_value = mock_output
        
        data = pd.DataFrame({"Close": [100.0] * 20})
        params = {
            'bb_length': 20, 
            'bb_variation_min': 2.0, 
            'bb_variation_max': 10.0, 
            'operation_type': SIGNAL_BUY
        }
        
        indicator = BollingerBandWidth(name="BW_Test", params=params)
        self.assertEqual(indicator.evaluate(data), SIGNAL_BUY)

    @patch("pandas_ta.bbands")
    def test_bandwidth_exceeds_max(self, mock_bb):
        """Bandwidth is 15.0, max is 10.0 -> Should return 0 (SIGNAL_HOLD)."""
        length = 20
        std = 2.0
        col_name = f"BBB_{length}_{std}_{std}" # Dynamic naming
        
        # Mocking 15% bandwidth
        mock_bb.return_value = pd.DataFrame({col_name: [15.0]}, index=[19])
        
        data = pd.DataFrame({"Close": [100.0] * 20})
        params = {
            'bb_length': length, 
            'bb_std': std, 
            'bb_variation_max': 10.0, # The cap
            'operation_type': 1    # SIGNAL_BUY
        }
        
        indicator = BollingerBandWidth(name="BW_Test", params=params)
        result = indicator.evaluate(data)
        
        # We expect 0 because 15 > 10
        self.assertEqual(result, 0, f"Expected HOLD (0) because 15.0 exceeds max 10.0, got {result}")