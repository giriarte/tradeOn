import unittest
from unittest.mock import patch
import pandas as pd
from indicators.constants import CLOSE_COLUMN, HIGH_COLUMN, LOW_COLUMN, OPEN_COLUMN, SIGNAL_SELL, SIGNAL_HOLD
from indicators.hangingMan import HangingMan

class TestHangingMan(unittest.TestCase):

    def setUp(self):
        """Initialize the indicator."""
        self.indicator_name = "HangingMan_Test"
        self.indicator = HangingMan(name=self.indicator_name)

    @patch("pandas_ta.cdl_pattern")
    def test_evaluate_red_hanging_man_returns_sell(self, mock_cdl):
        """Verify SIGNAL_SELL is returned when a Hanging Man is detected and the body is RED."""
        # Arrange: Mock library to find a Hanging Man (-100)
        mock_output = pd.DataFrame({"CDL_HANGINGMAN": [0.0, -100.0]}, index=[0, 1])
        mock_cdl.return_value = mock_output
        
        # Create a Red Candle (Close 101 < Open 105)
        # Long lower wick: Low is 90
        data = {
            OPEN_COLUMN:  [100.0, 105.0],
            HIGH_COLUMN:  [102.0, 106.0],
            LOW_COLUMN:   [98.0,  90.0],
            CLOSE_COLUMN: [101.0, 101.0]
        }
        df = pd.DataFrame(data, index=pd.date_range("2025-01-01", periods=2))

        # Act
        signal = self.indicator.evaluate(df)

        # Assert
        self.assertEqual(signal, SIGNAL_SELL)

    @patch("pandas_ta.cdl_pattern")
    def test_evaluate_green_hanging_man_returns_hold(self, mock_cdl):
        """Verify SIGNAL_HOLD is returned when a Hanging Man is detected but the body is GREEN."""
        # Arrange: Mock library to find a Hanging Man (-100)
        mock_output = pd.DataFrame({"CDL_HANGINGMAN": [0.0, -100.0]}, index=[0, 1])
        mock_cdl.return_value = mock_output
        
        # Create a Green Candle (Close 105 > Open 101)
        data = {
            OPEN_COLUMN:  [100.0, 101.0],
            HIGH_COLUMN:  [102.0, 106.0],
            LOW_COLUMN:   [98.0,  90.0],
            CLOSE_COLUMN: [101.0, 105.0]
        }
        df = pd.DataFrame(data, index=pd.date_range("2025-01-01", periods=2))

        # Act
        signal = self.indicator.evaluate(df)

        # Assert
        self.assertEqual(signal, SIGNAL_HOLD)

    @patch("pandas_ta.cdl_pattern")
    def test_evaluate_no_pattern_returns_hold(self, mock_cdl):
        """Verify SIGNAL_HOLD is returned when the library detects no pattern."""
        mock_output = pd.DataFrame({"CDL_HANGINGMAN": [0.0, 0.0]}, index=[0, 1])
        mock_cdl.return_value = mock_output
        
        data = {
            OPEN_COLUMN: [100, 105], HIGH_COLUMN: [106, 107], 
            LOW_COLUMN: [99, 104], CLOSE_COLUMN: [105, 106]
        }
        df = pd.DataFrame(data, index=pd.date_range("2025-01-01", periods=2))

        signal = self.indicator.evaluate(df)
        self.assertEqual(signal, SIGNAL_HOLD)
