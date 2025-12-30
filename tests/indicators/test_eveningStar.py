import unittest
from unittest.mock import patch
import pandas as pd
from indicators.constants import CLOSE_COLUMN, HIGH_COLUMN, LOW_COLUMN, OPEN_COLUMN, SIGNAL_SELL, SIGNAL_HOLD
from indicators.eveningStar import EveningStar

class TestEveningStar(unittest.TestCase):

    def setUp(self):
        """Initialize the indicator and dummy data."""
        self.indicator_name = "EveningStar_Test"
        self.indicator = EveningStar(name=self.indicator_name)
        
        # Evening Star is a 3-candle pattern, so we provide at least 3 rows
        self.df = pd.DataFrame({
            OPEN_COLUMN:  [100.0, 110.0, 108.0],
            HIGH_COLUMN:  [112.0, 115.0, 109.0],
            LOW_COLUMN:   [99.0,  109.0, 102.0],
            CLOSE_COLUMN: [110.0, 111.0, 103.0]
        }, index=pd.date_range("2025-01-01", periods=3))

    @patch("pandas_ta.cdl_pattern")
    def test_evaluate_evening_star_detection(self, mock_cdl):
        """Verify SIGNAL_SELL is returned when the library detects an Evening Star (-100)."""
        # Arrange: Mock pandas_ta to return -100 on the last index
        # The column name in pandas_ta for this is usually 'CDL_EVENINGSTAR'
        mock_output = pd.DataFrame({"CDL_EVENINGSTAR": [0.0, 0.0, -100.0]}, index=self.df.index)
        mock_cdl.return_value = mock_output

        # Act
        signal = self.indicator.evaluate(self.df)

        # Assert
        self.assertEqual(signal, SIGNAL_SELL)

    @patch("pandas_ta.cdl_pattern")
    def test_evaluate_no_pattern_returns_hold(self, mock_cdl):
        """Verify SIGNAL_HOLD is returned when no pattern is detected (0.0)."""
        # Arrange
        mock_output = pd.DataFrame({"CDL_EVENINGSTAR": [0.0, 0.0, 0.0]}, index=self.df.index)
        mock_cdl.return_value = mock_output

        # Act
        signal = self.indicator.evaluate(self.df)

        # Assert
        self.assertEqual(signal, SIGNAL_HOLD)

    @patch("pandas_ta.cdl_pattern")
    def test_evaluate_handles_unexpected_positive_value(self, mock_cdl):
        """
        Verify that even if the library returns a positive 100 
        (which shouldn't happen for Evening Star), our code stays neutral 
        unless it's specifically -100.
        """
        # Arrange
        mock_output = pd.DataFrame({"CDL_EVENINGSTAR": [0.0, 0.0, 100.0]}, index=self.df.index)
        mock_cdl.return_value = mock_output

        # Act
        signal = self.indicator.evaluate(self.df)

        # Assert
        self.assertEqual(signal, SIGNAL_HOLD)
