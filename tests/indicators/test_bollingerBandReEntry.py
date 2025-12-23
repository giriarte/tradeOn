import unittest
from unittest.mock import patch
import pandas as pd
from indicators.bollingerBandReEntry import BollingerBandReEntry
from indicators.constants import SIGNAL_BUY, SIGNAL_HOLD

class TestBollingerBandReEntry(unittest.TestCase):

    @patch("pandas_ta.bbands")
    def test_bullish_reentry_3_period(self, mock_bb):
        """Verify SIGNAL_BUY when price moves from below BBL(3) to inside."""
        # Setup: length=3, std=2.0
        # For a 3-period BB, the dataframe must have at least 4 rows
        length = 3
        std = 2.0
        
        # Mocking the BB DataFrame output with 3-period column names
        # Index -2 (prev): Price 90, BBL 100 -> Outside
        # Index -1 (curr): Price 105, BBL 100 -> Inside
        mock_output = pd.DataFrame({
            f"BBL_{length}_{std}_{std}": [100.0, 100.0, 100.0, 100.0],
            f"BBM_{length}_{std}_{std}": [110.0, 110.0, 110.0, 110.0],
            f"BBU_{length}_{std}_{std}": [120.0, 120.0, 120.0, 120.0]
        })
        mock_bb.return_value = mock_output
        
        # Dataframe with 4 rows to pass len(data) < (length + 1)
        data = pd.DataFrame({
            "Close": [110.0, 110.0, 90.0, 105.0]
        })
        
        params = {
            'bb_length': length, 
            'bb_std': std, 
            'operation_type': SIGNAL_BUY
        }
        
        indicator = BollingerBandReEntry(name="BB_ReEntry_3_Test", params=params)
        
        # Act
        signal = indicator.evaluate(data)
        
        # Assert
        self.assertEqual(signal, SIGNAL_BUY)

    @patch("pandas_ta.bbands")
    def test_no_signal_if_already_inside(self, mock_bb):
        """Verify SIGNAL_HOLD if price stays inside the bands."""
        mock_output = pd.DataFrame({
            "BBL_20_2.0_2.0": [100.0, 100.0],
            "BBM_20_2.0_2.0": [110.0, 110.0],
            "BBU_20_2.0_2.0": [120.0, 120.0]
        })
        mock_bb.return_value = mock_output
        
        data = pd.DataFrame({"Close": [105.0, 106.0]}) # Always inside
        params = {'bb_length': 20, 'bb_std': 2.0, 'operation_type': SIGNAL_BUY}
        
        indicator = BollingerBandReEntry(name="BB_Test", params=params)
        self.assertEqual(indicator.evaluate(data), SIGNAL_HOLD)
