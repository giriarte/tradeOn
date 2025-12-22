import unittest
import pandas as pd
from indicators.constants import SIGNAL_BUY, SIGNAL_HOLD
from indicators.dragonFlyDoji import DragonflyDoji
from unittest.mock import patch

class TestDragonFlyDoji(unittest.TestCase):
    """
    Unit tests for the DragonflyDoji indicator class using unittest.
    """

    def setUp(self):
        """
        Initialize the indicator before each test.
        """
        self.indicator_name = "Dragonfly_Test"
        self.params = {"threshold": 0.1}
        self.indicator = DragonflyDoji(name=self.indicator_name, params=self.params)
        self.dragonflyDf = pd.DataFrame({
            "Open": [100, 101, 102],
            "High": [105, 105, 105],
            "Low": [95, 95, 95],
            "Close": [102, 102, 102]
        }, index=pd.date_range("2023-01-01", periods=3))

    def get_dragonfly_data(self) -> pd.DataFrame:
        """
        Provides a preceding downtrend (110 -> 105 -> 100) 
        followed by the Dragonfly shape at the bottom.
        """
        data = {
            "Open":  [110.0, 105.0, 100.0, 105.0],
            "High":  [112.0, 107.0, 102.0, 105.0], # Final High = Open = Close
            "Low":   [108.0, 103.0, 98.0,  95.0],  # Long lower wick
            "Close": [105.0, 100.0, 101.0, 105.0]
        }
        return pd.DataFrame(data, index=pd.date_range("2023-01-01", periods=4))

    def get_neutral_data(self) -> pd.DataFrame:
        """
        Helper to generate a DataFrame with standard candles (No Doji).
        """
        data = {
            "Open":  [100.0, 102.0, 104.0],
            "High":  [103.0, 105.0, 107.0],
            "Low":   [99.0,  101.0, 103.0],
            "Close": [102.0, 104.0, 106.0]
        }
        return pd.DataFrame(data, index=pd.date_range("2023-01-01", periods=3))

    def test_initialization(self):
        """Verify the indicator initializes with correct name and params."""
        self.assertEqual(self.indicator.name, self.indicator_name)
        self.assertEqual(self.indicator.params, self.params)

    @patch("pandas_ta.cdl_pattern")
    def test_evaluate_returns_buy_signal(self, mock_cdl):
        """
        Force pandas_ta to return a positive result to test our 
        class logic independently of the library's strict internal rules.
        """
        # Create a mock return value that mimics the structure of pandas_ta output
        mock_output = pd.DataFrame({"CDL_DRAGONFLYDOJI": [0.0, 0.0, 100.0]}, index=self.dragonflyDf.index)
        mock_cdl.return_value = mock_output

        signal = self.indicator.evaluate(self.dragonflyDf)
        self.assertEqual(signal, SIGNAL_BUY)

    def test_evaluate_returns_hold_signal(self):
        """Verify SIGNAL_HOLD is returned when no pattern is present."""
        df = self.get_neutral_data()
        signal = self.indicator.evaluate(df)
        self.assertEqual(signal, SIGNAL_HOLD)

