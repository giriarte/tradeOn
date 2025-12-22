import unittest
from unittest.mock import MagicMock
import pandas as pd
from indicators.bearishCandlePattern import BearishCandlePattern
from indicators.constants import SIGNAL_SELL, SIGNAL_HOLD

class TestBearishCandlePattern(unittest.TestCase):

    def setUp(self):
        """Initialize the composite indicator and dummy data."""
        # Using a name as required by the Indicator base class
        self.indicator = BearishCandlePattern(name="Composite_Bearish_Test")
        self.df = pd.DataFrame({
            "Open": [100, 101], "High": [102, 103], 
            "Low": [98, 99], "Close": [99, 98]
        }, index=pd.date_range("2025-01-01", periods=2))

    def test_evaluate_returns_sell_if_one_indicator_triggers(self):
        """Verify that any single child trigger results in a composite SIGNAL_SELL."""
        # Setup mocks
        mock_shooting_star = MagicMock()
        mock_shooting_star.evaluate.return_value = SIGNAL_SELL
        
        mock_gravestone = MagicMock()
        mock_gravestone.evaluate.return_value = SIGNAL_HOLD
        
        # Inject mocks into the list
        self.indicator.bearish_indicators = [mock_gravestone, mock_shooting_star]

        signal = self.indicator.evaluate(self.df)
        
        self.assertEqual(signal, SIGNAL_SELL)

    def test_evaluate_returns_hold_if_none_trigger(self):
        """Verify the composite remains neutral if no children trigger."""
        for child in self.indicator.bearish_indicators:
            child.evaluate = MagicMock(return_value=SIGNAL_HOLD)

        signal = self.indicator.evaluate(self.df)
        self.assertEqual(signal, SIGNAL_HOLD)

    def test_evaluate_short_circuits_on_first_sell(self):
        """
        Verify that once a SELL signal is found, the remaining 
        indicators are not evaluated (Efficiency test).
        """
        # Create mocks for the evaluate methods specifically
        mock_eval_1 = MagicMock(return_value=SIGNAL_SELL)
        mock_eval_2 = MagicMock(return_value=SIGNAL_SELL)
        
        # Create dummy indicator objects
        indicator1 = MagicMock()
        indicator1.evaluate = mock_eval_1
        
        indicator2 = MagicMock()
        indicator2.evaluate = mock_eval_2
        
        # Order matters here: indicator1 should stop the loop before indicator2
        self.indicator.bearish_indicators = [indicator1, indicator2]
        
        # Act
        self.indicator.evaluate(self.df)
        
        # Assert
        mock_eval_1.assert_called_once()
        # This will now correctly pass because we are checking the method, 
        # not the comparison result of the return value.
        mock_eval_2.assert_not_called()
