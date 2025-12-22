import unittest
from unittest.mock import patch
import pandas as pd
from indicators.constants import SIGNAL_SELL, SIGNAL_HOLD
from indicators.shootingStar import ShootingStar

class TestShootingStar(unittest.TestCase):

    def setUp(self):
        """Initialize the indicator."""
        self.indicator_name = "ShootingStar_Test"
        self.indicator = ShootingStar(name=self.indicator_name)

    @patch("pandas_ta.cdl_pattern")
    def test_evaluate_red_shooting_star_returns_sell(self, mock_cdl):
        """Verify SIGNAL_SELL is returned when a Shooting Star is detected and the body is RED."""
        # Arrange: Mock library to find a Shooting Star (-100)
        mock_output = pd.DataFrame({"CDL_SHOOTINGSTAR": [0.0, -100.0]}, index=[0, 1])
        mock_cdl.return_value = mock_output
        
        # Create a Red Candle (Close 101 < Open 104)
        # Long upper wick: High is 120
        data = {
            "Open":  [100.0, 104.0],
            "High":  [105.0, 120.0],
            "Low":   [99.0,  100.0],
            "Close": [103.0, 101.0]
        }
        df = pd.DataFrame(data, index=pd.date_range("2025-01-01", periods=2))

        # Act
        signal = self.indicator.evaluate(df)

        # Assert
        self.assertEqual(signal, SIGNAL_SELL)

    @patch("pandas_ta.cdl_pattern")
    def test_evaluate_green_shooting_star_returns_hold(self, mock_cdl):
        """Verify SIGNAL_HOLD is returned when a Shooting Star is detected but the body is GREEN."""
        # Arrange: Mock library to find a Shooting Star (-100)
        mock_output = pd.DataFrame({"CDL_SHOOTINGSTAR": [0.0, -100.0]}, index=[0, 1])
        mock_cdl.return_value = mock_output
        
        # Create a Green Candle (Close 105 > Open 102)
        data = {
            "Open":  [100.0, 102.0],
            "High":  [105.0, 120.0],
            "Low":   [99.0,  101.0],
            "Close": [103.0, 105.0]
        }
        df = pd.DataFrame(data, index=pd.date_range("2025-01-01", periods=2))

        # Act
        signal = self.indicator.evaluate(df)

        # Assert
        self.assertEqual(signal, SIGNAL_HOLD)

    @patch("pandas_ta.cdl_pattern")
    def test_evaluate_no_pattern_returns_hold(self, mock_cdl):
        """Verify SIGNAL_HOLD is returned when the library detects no pattern."""
        mock_output = pd.DataFrame({"CDL_SHOOTINGSTAR": [0.0, 0.0]}, index=[0, 1])
        mock_cdl.return_value = mock_output
        
        data = {
            "Open": [100, 105], "High": [106, 107], 
            "Low": [99, 104], "Close": [105, 106]
        }
        df = pd.DataFrame(data, index=pd.date_range("2025-01-01", periods=2))

        signal = self.indicator.evaluate(df)
        self.assertEqual(signal, SIGNAL_HOLD)
