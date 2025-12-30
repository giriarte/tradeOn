import unittest
from unittest.mock import patch
import pandas as pd
from indicators.constants import CLOSE_COLUMN, HIGH_COLUMN, LOW_COLUMN, OPEN_COLUMN, SIGNAL_BUY, SIGNAL_HOLD
from indicators.morningStar import MorningStar

class TestMorningStar(unittest.TestCase):

    def setUp(self):
        """Initialize the indicator and dummy data."""
        self.indicator_name = "MorningStar_Test"
        self.indicator = MorningStar(name=self.indicator_name)
        
        # Morning Star requires a 3-candle sequence
        # Candle 1: Large Bearish
        # Candle 2: Small Body (Indecision)
        # Candle 3: Large Bullish
        self.df = pd.DataFrame({
            OPEN_COLUMN:  [110.0, 100.0, 102.0],
            HIGH_COLUMN:  [111.0, 101.0, 108.0],
            LOW_COLUMN:   [100.0, 98.0,  101.0],
            CLOSE_COLUMN: [101.0, 99.0,  107.0]
        }, index=pd.date_range("2025-01-01", periods=3))

    @patch("pandas_ta.cdl_pattern")
    def test_evaluate_morning_star_detection(self, mock_cdl):
        """Verify SIGNAL_BUY is returned when the library detects a Morning Star (100)."""
        # Arrange: Mock pandas_ta to return 100 on the last index (the 3rd candle)
        # The column name in pandas_ta is typically 'CDL_MORNINGSTAR'
        mock_output = pd.DataFrame({"CDL_MORNINGSTAR": [0.0, 0.0, 100.0]}, index=self.df.index)
        mock_cdl.return_value = mock_output

        # Act
        signal = self.indicator.evaluate(self.df)

        # Assert
        self.assertEqual(signal, SIGNAL_BUY)

    @patch("pandas_ta.cdl_pattern")
    def test_evaluate_no_pattern_returns_hold(self, mock_cdl):
        """Verify SIGNAL_HOLD is returned when no pattern is detected (0.0)."""
        # Arrange
        mock_output = pd.DataFrame({"CDL_MORNINGSTAR": [0.0, 0.0, 0.0]}, index=self.df.index)
        mock_cdl.return_value = mock_output

        # Act
        signal = self.indicator.evaluate(self.df)

        # Assert
        self.assertEqual(signal, SIGNAL_HOLD)

    @patch("pandas_ta.cdl_pattern")
    def test_evaluate_handles_bearish_value(self, mock_cdl):
        """
        Verify that our MorningStar class stays neutral if an unexpected 
        bearish value (-100) is returned (though Morning Star is inherently bullish).
        """
        # Arrange
        mock_output = pd.DataFrame({"CDL_MORNINGSTAR": [0.0, 0.0, -100.0]}, index=self.df.index)
        mock_cdl.return_value = mock_output

        # Act
        signal = self.indicator.evaluate(self.df)

        # Assert
        self.assertEqual(signal, SIGNAL_HOLD)
