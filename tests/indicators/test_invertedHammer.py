import unittest
from unittest.mock import patch
import pandas as pd
from indicators.InvertedHammer import InvertedHammer
from indicators.constants import CLOSE_COLUMN, HIGH_COLUMN, LOW_COLUMN, OPEN_COLUMN, SIGNAL_BUY, SIGNAL_HOLD

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
            OPEN_COLUMN:  [110.0, 101.0],
            HIGH_COLUMN:  [112.0, 115.0],
            LOW_COLUMN:   [108.0, 100.5],
            CLOSE_COLUMN: [105.0, 102.0]
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
            OPEN_COLUMN:  [110.0, 101.0],
            HIGH_COLUMN:  [112.0, 115.0],
            LOW_COLUMN:   [108.0, 99.5],
            CLOSE_COLUMN: [105.0, 100.0]
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
            OPEN_COLUMN: [100, 101], HIGH_COLUMN: [102, 103], 
            LOW_COLUMN: [98, 99], CLOSE_COLUMN: [101, 102]
        }
        df = pd.DataFrame(data, index=pd.date_range("2025-01-01", periods=2))

        signal = self.indicator.evaluate(df)
        self.assertEqual(signal, SIGNAL_HOLD)
