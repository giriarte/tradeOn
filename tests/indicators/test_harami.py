import unittest
from unittest.mock import patch
import pandas as pd
from indicators.constants import CLOSE_COLUMN, HIGH_COLUMN, LOW_COLUMN, OPEN_COLUMN, SIGNAL_BUY, SIGNAL_SELL, SIGNAL_HOLD
from indicators.harami import Harami

class TestHarami(unittest.TestCase):

    def setUp(self):
        """Initialize the indicator and dummy data."""
        self.indicator_name = "Harami_Test"
        self.indicator = Harami(name=self.indicator_name)
        
        # Harami is a two-candle pattern (Mother and Baby)
        self.df = pd.DataFrame({
            OPEN_COLUMN:  [100.0, 102.0],
            HIGH_COLUMN:  [105.0, 104.0],
            LOW_COLUMN:   [95.0,  96.0],
            CLOSE_COLUMN: [96.0,  103.0]
        }, index=pd.date_range("2025-01-01", periods=2))

    @patch("pandas_ta.cdl_pattern")
    def test_evaluate_bullish_harami(self, mock_cdl):
        """Verify SIGNAL_BUY is returned when the library detects a Bullish Harami (100)."""
        # Mocking the output of pandas_ta.cdl_pattern(name="harami")
        mock_output = pd.DataFrame({"CDL_HARAMI": [0.0, 100.0]}, index=self.df.index)
        mock_cdl.return_value = mock_output

        signal = self.indicator.evaluate(self.df)
        self.assertEqual(signal, SIGNAL_BUY)

    @patch("pandas_ta.cdl_pattern")
    def test_evaluate_bearish_harami(self, mock_cdl):
        """Verify SIGNAL_SELL is returned when the library detects a Bearish Harami (-100)."""
        mock_output = pd.DataFrame({"CDL_HARAMI": [0.0, -100.0]}, index=self.df.index)
        mock_cdl.return_value = mock_output

        signal = self.indicator.evaluate(self.df)
        self.assertEqual(signal, SIGNAL_SELL)

    @patch("pandas_ta.cdl_pattern")
    def test_evaluate_no_pattern(self, mock_cdl):
        """Verify SIGNAL_HOLD is returned when no pattern is detected (0.0)."""
        mock_output = pd.DataFrame({"CDL_HARAMI": [0.0, 0.0]}, index=self.df.index)
        mock_cdl.return_value = mock_output

        signal = self.indicator.evaluate(self.df)
        self.assertEqual(signal, SIGNAL_HOLD)

    @patch("pandas_ta.cdl_pattern")
    def test_evaluate_handles_unexpected_data(self, mock_cdl):
        """Verify robustness when the library returns an empty DataFrame."""
        mock_cdl.return_value = pd.DataFrame()
        
        signal = self.indicator.evaluate(self.df)
        self.assertEqual(signal, SIGNAL_HOLD)
