import unittest
from unittest.mock import patch
import pandas as pd
from indicators.constants import SIGNAL_SELL, SIGNAL_HOLD
from indicators.gravestoneDoji import GravestoneDoji

class TestGravestoneDoji(unittest.TestCase):

    def setUp(self):
        """Initialize the indicator and dummy data."""
        self.indicator_name = "GravestoneDoji_Test"
        self.indicator = GravestoneDoji(name=self.indicator_name)
        
        # We provide 3 rows to simulate a short time series
        self.df = pd.DataFrame({
            "Open":  [100.0, 102.0, 105.0],
            "High":  [103.0, 105.0, 115.0], # Final candle has long upper wick
            "Low":   [98.0,  101.0, 105.0], # Final candle Low = Open = Close
            "Close": [102.0, 104.0, 105.0]
        }, index=pd.date_range("2025-01-01", periods=3))

    @patch("pandas_ta.cdl_pattern")
    def test_evaluate_gravestone_doji_detection(self, mock_cdl):
        """Verify SIGNAL_SELL is returned when the library detects the pattern (100)."""
        # Arrange: Mock pandas_ta to return 100 on the last index
        mock_output = pd.DataFrame({"CDL_GRAVESTONEDOJI": [0.0, 0.0, 100.0]}, index=self.df.index)
        mock_cdl.return_value = mock_output

        # Act
        signal = self.indicator.evaluate(self.df)

        # Assert
        self.assertEqual(signal, SIGNAL_SELL)

    @patch("pandas_ta.cdl_pattern")
    def test_evaluate_no_pattern_returns_hold(self, mock_cdl):
        """Verify SIGNAL_HOLD is returned when no pattern is detected (0.0)."""
        # Arrange
        mock_output = pd.DataFrame({"CDL_GRAVESTONEDOJI": [0.0, 0.0, 0.0]}, index=self.df.index)
        mock_cdl.return_value = mock_output

        # Act
        signal = self.indicator.evaluate(self.df)

        # Assert
        self.assertEqual(signal, SIGNAL_HOLD)

    @patch("pandas_ta.cdl_pattern")
    def test_evaluate_handles_none_gracefully(self, mock_cdl):
        """Verify that the indicator handles a None return from the library."""
        # Arrange
        mock_cdl.return_value = None

        # Act
        signal = self.indicator.evaluate(self.df)

        # Assert
        self.assertEqual(signal, SIGNAL_HOLD)
