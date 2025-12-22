import unittest
from unittest.mock import patch
import pandas as pd
from indicators.InvertedHammer import InvertedHammer
from indicators.constants import SIGNAL_BUY, SIGNAL_HOLD

class TestInvertedHammer(unittest.TestCase):

    def setUp(self):
        """Initialize the indicator."""
        self.indicator_name = "InvertedHammer_Test"
        self.indicator = InvertedHammer(name=self.indicator_name)

    @patch("pandas_ta.cdl_pattern")
    def test_evaluate_green_inverted_hammer_returns_buy(self, mock_cdl):
        """Verify SIGNAL_BUY is returned when an Inverted Hammer is detected and the body is GREEN."""
        # Arrange: Mock library to find an Inverted Hammer (100)
        mock_output = pd.DataFrame({"CDL_INVERTEDHAMMER": [0.0, 100.0]}, index=[0, 1])
        mock_cdl.return_value = mock_output
        
        # Create a Green Candle (Close 102 > Open 101)
        # Long upper wick: High is 115
        data = {
            "Open":  [110.0, 101.0],
            "High":  [112.0, 115.0],
            "Low":   [108.0, 100.5],
            "Close": [105.0, 102.0]
        }
        df = pd.DataFrame(data, index=pd.date_range("2025-01-01", periods=2))

        # Act
        signal = self.indicator.evaluate(df)

        # Assert
        self.assertEqual(signal, SIGNAL_BUY)

    @patch("pandas_ta.cdl_pattern")
    def test_evaluate_red_inverted_hammer_returns_hold(self, mock_cdl):
        """Verify SIGNAL_HOLD is returned when an Inverted Hammer is detected but the body is RED."""
        # Arrange: Mock library to find an Inverted Hammer (100)
        mock_output = pd.DataFrame({"CDL_INVERTEDHAMMER": [0.0, 100.0]}, index=[0, 1])
        mock_cdl.return_value = mock_output
        
        # Create a Red Candle (Close 100 < Open 101)
        data = {
            "Open":  [110.0, 101.0],
            "High":  [112.0, 115.0],
            "Low":   [108.0, 99.5],
            "Close": [105.0, 100.0]
        }
        df = pd.DataFrame(data, index=pd.date_range("2025-01-01", periods=2))

        # Act
        signal = self.indicator.evaluate(df)

        # Assert
        self.assertEqual(signal, SIGNAL_HOLD)

    @patch("pandas_ta.cdl_pattern")
    def test_evaluate_no_pattern_returns_hold(self, mock_cdl):
        """Verify SIGNAL_HOLD is returned when the library detects no pattern."""
        mock_output = pd.DataFrame({"CDL_INVERTEDHAMMER": [0.0, 0.0]}, index=[0, 1])
        mock_cdl.return_value = mock_output
        
        data = {
            "Open": [100, 101], "High": [102, 103], 
            "Low": [98, 99], "Close": [101, 102]
        }
        df = pd.DataFrame(data, index=pd.date_range("2025-01-01", periods=2))

        signal = self.indicator.evaluate(df)
        self.assertEqual(signal, SIGNAL_HOLD)
