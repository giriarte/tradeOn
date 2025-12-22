import unittest
import pandas as pd
from indicators.constants import (
    OPEN_COLUMN,
    CLOSE_COLUMN,
    N_CANDLES_LENGTH,
    N_CANDLES_OPERATION,
    N_CANDLES_OFFSET,
    SIGNAL_BUY,
    SIGNAL_SELL,
    SIGNAL_HOLD
)
from indicators.nRedCandles import NRedCandles

class TestNRedCandles(unittest.TestCase):

    def setUp(self):
        """Initialize the indicator with a standard buy configuration."""
        self.indicator_name = "N_Red_Test"
        self.params = {
            N_CANDLES_LENGTH: 3,
            N_CANDLES_OPERATION: SIGNAL_BUY,
            N_CANDLES_OFFSET: 0
        }
        self.indicator = NRedCandles(name=self.indicator_name, params=self.params)

    def test_evaluate_returns_buy_for_n_red_candles(self):
        """Verify SIGNAL_BUY when exactly N candles are red (Close < Open)."""
        data = {
            OPEN_COLUMN:  [101, 102, 103],
            CLOSE_COLUMN: [100, 101, 102]  # All Red
        }
        df = pd.DataFrame(data)
        
        signal = self.indicator.evaluate(df)
        self.assertEqual(signal, SIGNAL_BUY)

    def test_evaluate_returns_hold_if_one_is_green(self):
        """Verify SIGNAL_HOLD if a single candle in the sequence is green."""
        data = {
            OPEN_COLUMN:  [101, 100, 103],
            CLOSE_COLUMN: [100, 101, 102]  # Middle candle is Green (101 > 100)
        }
        df = pd.DataFrame(data)
        
        signal = self.indicator.evaluate(df)
        self.assertEqual(signal, SIGNAL_HOLD)

    def test_evaluate_with_offset_logic(self):
        """Verify that the offset Y correctly skips the most recent candles."""
        # Check for 2 red candles, skipping the most recent 1
        params = {
            N_CANDLES_LENGTH: 2,
            N_CANDLES_OPERATION: SIGNAL_BUY,
            N_CANDLES_OFFSET: 1
        }
        data = {
            OPEN_COLUMN:  [105, 104, 100], # Rows 0, 1 are Red
            CLOSE_COLUMN: [104, 103, 105]  # Row 2 is Green
        }
        df = pd.DataFrame(data)
        
        # With Offset 1, we ignore Row 2 and look at Rows 0 & 1
        signal = self.indicator.evaluate(df, params=params)
        self.assertEqual(signal, SIGNAL_BUY)

    def test_evaluate_custom_sell_operation(self):
        """Verify it returns SIGNAL_SELL when the operation parameter is changed."""
        params = {
            N_CANDLES_LENGTH: 2,
            N_CANDLES_OPERATION: SIGNAL_SELL
        }
        data = {
            OPEN_COLUMN:  [110, 109],
            CLOSE_COLUMN: [109, 108]
        }
        df = pd.DataFrame(data)
        
        signal = self.indicator.evaluate(df, params=params)
        self.assertEqual(signal, SIGNAL_SELL)

    def test_insufficient_data_returns_hold(self):
        """Verify return 0 if DataFrame length is less than lookback N."""
        data = {
            OPEN_COLUMN:  [100, 101],
            CLOSE_COLUMN: [99, 100]
        }
        df = pd.DataFrame(data)
        
        # N=3 (default), but only 2 rows provided
        signal = self.indicator.evaluate(df)
        self.assertEqual(signal, SIGNAL_HOLD)

    def test_missing_columns_returns_hold(self):
        """Verify the class returns 0 and prints error if columns are missing."""
        df = pd.DataFrame({"High": [100, 101], "Low": [90, 91]})
        
        signal = self.indicator.evaluate(df)
        self.assertEqual(signal, SIGNAL_HOLD)
