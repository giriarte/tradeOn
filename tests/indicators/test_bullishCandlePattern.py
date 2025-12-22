import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from indicators.bullishCandlePattern import BullishCandlePattern
from indicators.constants import SIGNAL_BUY, SIGNAL_HOLD

class TestBullishCandlePattern(unittest.TestCase):

    def setUp(self):
        """Initialize the composite indicator and dummy data."""
        self.indicator = BullishCandlePattern(name="Composite_Bullish_Test")
        self.df = pd.DataFrame({
            "Open": [100, 101], "High": [102, 103], 
            "Low": [98, 99], "Close": [101, 102]
        }, index=pd.date_range("2025-01-01", periods=2))

    def test_evaluate_returns_buy_if_one_indicator_triggers(self):
        """
        Verify that if any child indicator returns SIGNAL_BUY, 
        the composite returns SIGNAL_BUY.
        """
        # We mock the internal list of indicators
        mock_hammer = MagicMock()
        mock_hammer.evaluate.return_value = SIGNAL_BUY
        
        mock_harami = MagicMock()
        mock_harami.evaluate.return_value = SIGNAL_HOLD
        
        # Inject our mocks into the indicator instance
        self.indicator.bullish_indicators = [mock_harami, mock_hammer]

        signal = self.indicator.evaluate(self.df)
        
        # Should be BUY because the hammer triggered
        self.assertEqual(signal, SIGNAL_BUY)

    def test_evaluate_returns_hold_if_none_trigger(self):
        """Verify the composite returns SIGNAL_HOLD if all children return HOLD."""
        for child in self.indicator.bullish_indicators:
            child.evaluate = MagicMock(return_value=SIGNAL_HOLD)

        signal = self.indicator.evaluate(self.df)
        self.assertEqual(signal, SIGNAL_HOLD)

    def test_evaluate_stops_at_first_buy(self):
        """
        Performance check: Verify that the loop exits early 
        as soon as a BUY signal is found.
        """
        # Create mocks for the evaluate method specifically
        mock_1 = MagicMock(return_value=SIGNAL_BUY)
        mock_2 = MagicMock(return_value=SIGNAL_BUY)
        
        # Manually assign these mocks to the 'evaluate' attribute of dummy objects
        indicator1 = MagicMock()
        indicator1.evaluate = mock_1
        
        indicator2 = MagicMock()
        indicator2.evaluate = mock_2
        
        self.indicator.bullish_indicators = [indicator1, indicator2]
        
        # Act
        self.indicator.evaluate(self.df)
        
        # Assert: Only the first indicator's evaluate should have been called
        self.assertTrue(mock_1.called, "The first indicator should have been evaluated.")
        self.assertFalse(mock_2.called, "The second indicator should NOT have been evaluated (short-circuit).")
