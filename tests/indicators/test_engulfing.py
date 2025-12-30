import unittest
from unittest.mock import patch
import pandas as pd
from indicators.constants import CLOSE_COLUMN, HIGH_COLUMN, LOW_COLUMN, OPEN_COLUMN, SIGNAL_BUY, SIGNAL_SELL, SIGNAL_HOLD
from indicators.engulfing import Engulfing

class TestEngulfing(unittest.TestCase):

    def setUp(self):
        """Initialize the indicator and dummy data."""
        self.indicator_name = "Engulfing_Test"
        self.indicator = Engulfing(name=self.indicator_name)
        
        # Engulfing is a 2-candle pattern, so we provide at least 2 rows
        self.df = pd.DataFrame({
            OPEN_COLUMN: [100.0, 105.0],
            HIGH_COLUMN: [106.0, 106.0],
            LOW_COLUMN: [99.0, 94.0],
            CLOSE_COLUMN: [104.0, 95.0]
        }, index=pd.date_range("2025-01-01", periods=2))

    @patch("pandas_ta.cdl_pattern")
    def test_evaluate_bullish_engulfing(self, mock_cdl):
        """Verify SIGNAL_BUY is returned when library returns 100."""
        # Mocking the DataFrame returned by pandas_ta.cdl_pattern(name="engulfing")
        # Column names often vary based on implementation, but your code uses .iloc[-1].values[0]
        mock_output = pd.DataFrame({"CDL_ENGULFING": [0.0, 100.0]}, index=self.df.index)
        mock_cdl.return_value = mock_output

        signal = self.indicator.evaluate(self.df)
        self.assertEqual(signal, SIGNAL_BUY)

    @patch("pandas_ta.cdl_pattern")
    def test_evaluate_bearish_engulfing(self, mock_cdl):
        """Verify SIGNAL_SELL is returned when library returns -100."""
        mock_output = pd.DataFrame({"CDL_ENGULFING": [0.0, -100.0]}, index=self.df.index)
        mock_cdl.return_value = mock_output

        signal = self.indicator.evaluate(self.df)
        self.assertEqual(signal, SIGNAL_SELL)

    @patch("pandas_ta.cdl_pattern")
    def test_evaluate_no_pattern(self, mock_cdl):
        """Verify SIGNAL_HOLD is returned when library returns 0."""
        mock_output = pd.DataFrame({"CDL_ENGULFING": [0.0, 0.0]}, index=self.df.index)
        mock_cdl.return_value = mock_output

        signal = self.indicator.evaluate(self.df)
        self.assertEqual(signal, SIGNAL_HOLD)

    @patch("pandas_ta.cdl_pattern")
    def test_evaluate_empty_or_none_returns_hold(self, mock_cdl):
        """Verify robustness when library returns None or empty result."""
        mock_cdl.return_value = None
        signal = self.indicator.evaluate(self.df)
        self.assertEqual(signal, SIGNAL_HOLD)
