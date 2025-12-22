import unittest
from unittest.mock import patch
import pandas as pd
from indicators.constants import (
    OPERATION_TYPE,
    SIGNAL_BUY,
    SIGNAL_HOLD,
    SIGNAL_SELL
)
from indicators.doji import Doji

class TestDoji(unittest.TestCase):

    def setUp(self):
        """Initialize the indicator and a dummy DataFrame."""
        self.indicator_name = "Doji_Test"
        # We use a 3-row DF to simulate time series data
        self.df = pd.DataFrame({
            "Open": [100.0, 101.0, 102.0],
            "High": [105.0, 105.0, 105.0],
            "Low": [95.0, 95.0, 95.0],
            "Close": [101.0, 100.0, 102.0]
        }, index=pd.date_range("2025-01-01", periods=3))

    @patch("pandas_ta.cdl_pattern")
    def test_evaluate_buy_mode_detection(self, mock_cdl):
        """Test that Doji returns SIGNAL_BUY when operationType is SIGNAL_BUY."""
        # Arrange: Mock pandas_ta to return 100 on the last candle
        mock_output = pd.DataFrame({"CDL_DOJI": [0.0, 0.0, 100.0]}, index=self.df.index)
        mock_cdl.return_value = mock_output
        
        params = {OPERATION_TYPE: SIGNAL_BUY}
        indicator = Doji(name=self.indicator_name, params=params)

        # Act
        signal = indicator.evaluate(self.df)

        # Assert
        self.assertEqual(signal, SIGNAL_BUY)

    @patch("pandas_ta.cdl_pattern")
    def test_evaluate_sell_mode_detection(self, mock_cdl):
        """Test that Doji returns SIGNAL_SELL when operationType is SIGNAL_SELL."""
        # Arrange: Mock pandas_ta to return 100
        mock_output = pd.DataFrame({"CDL_DOJI": [0.0, 0.0, 100.0]}, index=self.df.index)
        mock_cdl.return_value = mock_output
        
        params = {OPERATION_TYPE: SIGNAL_SELL}
        indicator = Doji(name=self.indicator_name, params=params)

        # Act
        signal = indicator.evaluate(self.df)

        # Assert
        self.assertEqual(signal, SIGNAL_SELL)

    @patch("pandas_ta.cdl_pattern")
    def test_evaluate_no_doji_returns_hold(self, mock_cdl):
        """Test that SIGNAL_HOLD is returned if the library detects no pattern (0.0)."""
        # Arrange: Mock pandas_ta to return 0.0
        mock_output = pd.DataFrame({"CDL_DOJI": [0.0, 0.0, 0.0]}, index=self.df.index)
        mock_cdl.return_value = mock_output
        
        indicator = Doji(name=self.indicator_name)

        # Act
        signal = indicator.evaluate(self.df)

        # Assert
        self.assertEqual(signal, SIGNAL_HOLD)

    @patch("pandas_ta.cdl_pattern")
    def test_evaluate_param_override(self, mock_cdl):
        """Test that providing params in evaluate() overrides instance params."""
        # Arrange
        mock_output = pd.DataFrame({"CDL_DOJI": [0.0, 0.0, 100.0]}, index=self.df.index)
        mock_cdl.return_value = mock_output
        
        # Instance is configured for BUY, but we will pass SELL in evaluate
        indicator = Doji(name=self.indicator_name, params={OPERATION_TYPE: SIGNAL_BUY})
        
        # Act
        signal = indicator.evaluate(self.df, params={OPERATION_TYPE: SIGNAL_SELL})

        # Assert
        self.assertEqual(signal, SIGNAL_SELL)
