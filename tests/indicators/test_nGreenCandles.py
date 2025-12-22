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
from indicators.nGreenCandles import NGreenCandles

class TestNGreenCandles(unittest.TestCase):

    def setUp(self):
        """Initialize the indicator and columns."""
        self.indicator_name = "N_Green_Test"
        self.params = {
            N_CANDLES_LENGTH: 3,
            N_CANDLES_OPERATION: SIGNAL_BUY,
            N_CANDLES_OFFSET: 0
        }
        self.indicator = NGreenCandles(name=self.indicator_name, params=self.params)

    def test_evaluate_returns_buy_for_n_green_candles(self):
        """Verify SIGNAL_BUY when exactly N candles are green with 0 offset."""
        data = {
            OPEN_COLUMN:  [100, 101, 102],
            CLOSE_COLUMN: [101, 102, 103]  # All Green
        }
        df = pd.DataFrame(data)
        
        signal = self.indicator.evaluate(df)
        self.assertEqual(signal, SIGNAL_BUY)

    def test_evaluate_returns_hold_if_one_is_red(self):
        """Verify SIGNAL_HOLD if at least one candle in the sequence is red."""
        data = {
            OPEN_COLUMN:  [100, 105, 102],
            CLOSE_COLUMN: [101, 104, 103]  # Middle candle is Red (104 < 105)
        }
        df = pd.DataFrame(data)
        
        signal = self.indicator.evaluate(df)
        self.assertEqual(signal, SIGNAL_HOLD)

    def test_evaluate_with_offset(self):
        """Verify logic when N_CANDLES_OFFSET is used (looking back from the past)."""
        # We want 2 green candles, but ignoring the most recent one (offset 1)
        params = {
            N_CANDLES_LENGTH: 2,
            N_CANDLES_OPERATION: SIGNAL_BUY,
            N_CANDLES_OFFSET: 1
        }
        data = {
            OPEN_COLUMN:  [100, 101, 110], # Row 0, 1 are green
            CLOSE_COLUMN: [101, 102, 105]  # Row 2 is red
        }
        df = pd.DataFrame(data)
        
        # Row 2 is current (offset 0), Row 1 & 0 are the window (offset 1)
        signal = self.indicator.evaluate(df, params=params)
        self.assertEqual(signal, SIGNAL_BUY, "Should trigger because the candles BEFORE the offset are green")

    def test_evaluate_returns_sell_operation(self):
        """Verify it returns SIGNAL_SELL if operation type is configured for sell."""
        params = {
            N_CANDLES_LENGTH: 2,
            N_CANDLES_OPERATION: SIGNAL_SELL,
            N_CANDLES_OFFSET: 0
        }
        data = {
            OPEN_COLUMN:  [100, 101],
            CLOSE_COLUMN: [101, 102]
        }
        df = pd.DataFrame(data)
        
        signal = self.indicator.evaluate(df, params=params)
        self.assertEqual(signal, SIGNAL_SELL)

    def test_insufficient_data_returns_hold(self):
        """Verify it returns HOLD if the dataframe is shorter than N candles."""
        data = {
            OPEN_COLUMN:  [100],
            CLOSE_COLUMN: [101]
        }
        df = pd.DataFrame(data)
        
        # N=3, but data length is 1
        signal = self.indicator.evaluate(df)
        self.assertEqual(signal, 0)

    def test_validation_errors(self):
        """Verify that missing parameters or columns raise ValueErrors."""
        df = pd.DataFrame({"WrongColumn": [1, 2]})
        
        with self.assertRaises(ValueError):
            self.indicator.evaluate(df)
