import unittest
import pandas as pd
from indicators.nRedCandles import NRedCandles
from indicators.constants import ( 
    N_CANDLES_LENGTH,
    N_CANDLES_OPERATION
)

class TestNRedCandles(unittest.TestCase):
    
    def setUp(self):
        """Initialize the indicator and common candle data fixtures."""
        self.indicator = NRedCandles()

        # Candle Definitions
        self.red_candle = {'Open': 100, 'Close': 99}   # Red (Bearish)
        self.green_candle = {'Open': 100, 'Close': 101} # Green (Bullish)
        self.doji_candle = {'Open': 100, 'Close': 100}  # Doji/Neutral (Not Red)

        # --- Data Scenario 1: Successful Match (Last N are Red) ---
        data_match = [
            self.green_candle, 
            self.red_candle, 
            self.red_candle, 
            self.red_candle  # Last 3 are RED
        ]
        self.df_match = pd.DataFrame(data_match)

        # --- Data Scenario 2: Failure (One Green Candle Breaks Sequence) ---
        data_fail_green = [
            self.red_candle, 
            self.red_candle, 
            self.green_candle, # Fails the condition
            self.red_candle
        ]
        self.df_fail_green = pd.DataFrame(data_fail_green)

        # --- Data Scenario 3: Failure (Doji Candle Breaks Sequence) ---
        data_fail_doji = [
            self.red_candle, 
            self.doji_candle, # Fails the condition
            self.red_candle, 
            self.red_candle
        ]
        self.df_fail_doji = pd.DataFrame(data_fail_doji)
        
        # --- Data Scenario 4: Insufficient Data ---
        data_short = [self.red_candle, self.red_candle]
        self.df_short = pd.DataFrame(data_short)
        
        # --- Data Scenario 5: Data with missing columns ---
        self.df_bad_cols = pd.DataFrame({'Price': [100, 101], 'Volume': [1, 2]})


    def test_successful_buy_signal_default_n(self):
        """Test case where the last 3 (default N) candles are red."""
        params = {N_CANDLES_LENGTH: 3}
        result = self.indicator.evaluate(self.df_match, params)
        # Expect 1 (default n_candles_operation is 1 for Buy)
        self.assertEqual(result, 1, "Should return 1 when last 3 candles are red")

    def test_successful_buy_signal_custom_n(self):
        """Test case with a custom N (4 candles)."""
        # Data df_fail_green has 4 candles: [R, R, G, R]. Check N=1 (R) -> Success
        params = {N_CANDLES_LENGTH: 1}
        result = self.indicator.evaluate(self.df_fail_green, params)
        self.assertEqual(result, 1, "Should return 1 when N=1 and the last candle is red")
        
    def test_failure_due_to_green_candle(self):
        """Test case where one of the last N is green (Close > Open)."""
        # Last 3 in df_fail_green are [R, G, R] -> Fail
        params = {N_CANDLES_LENGTH: 3}
        result = self.indicator.evaluate(self.df_fail_green, params)
        self.assertEqual(result, 0, "Should return 0 due to a green candle breaking the sequence")
        
    def test_failure_due_to_doji_candle(self):
        """Test case where one of the last N is a doji (Close = Open)."""
        # Last 3 in df_fail_doji are [Doji, R, R] -> Fail
        params = {N_CANDLES_LENGTH: 3}
        result = self.indicator.evaluate(self.df_fail_doji, params)
        self.assertEqual(result, 0, "Should return 0 due to a doji candle breaking the sequence")

    def test_insufficient_data(self):
        """Test case where data length is less than N."""
        # Data has 2 rows, N is 3 -> Fail
        params = {N_CANDLES_LENGTH: 3}
        result = self.indicator.evaluate(self.df_short, params)
        self.assertEqual(result, 0, "Should return 0 when data length is less than n_candles")

    def test_custom_operation_signal(self):
        """Test case where n_candles_operation is set to 2 (Sell signal)."""
        # Condition is met (last 3 are red)
        params = {N_CANDLES_LENGTH: 3, N_CANDLES_OPERATION: 2}
        result = self.indicator.evaluate(self.df_match, params)
        self.assertEqual(result, 2, "Should return 2 when n_candles_operation is 2")

    def test_missing_required_columns(self):
        """Test case for DataFrame missing 'Open' or 'Close'."""
        params = {N_CANDLES_LENGTH: 1}
        result = self.indicator.evaluate(self.df_bad_cols, params)
        self.assertEqual(result, 0, "Should return 0 when required columns are missing")
    