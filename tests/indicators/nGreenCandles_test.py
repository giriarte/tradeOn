import unittest
import pandas as pd
from indicators.nGreenCandles import NGreenCandles
from indicators.constants import ( 
    N_CANDLES_LENGTH,
    N_CANDLES_OPERATION
)

class TestNGreenCandles(unittest.TestCase):
    
    def setUp(self):
        """Set up the indicator object and various data scenarios for testing."""
        self.indicator = NGreenCandles()

        # Helper: Create a green candle (Close > Open)
        self.green_candle = {'Open': 100, 'Close': 101}
        # Helper: Create a red candle (Close < Open)
        self.red_candle = {'Open': 100, 'Close': 99}
        # Helper: Create a doji/neutral candle (Close = Open) - Treated as not green
        self.doji_candle = {'Open': 100, 'Close': 100}
        
        # --- Data Scenario 1: Perfect match (all green) ---
        data_match = [
            self.red_candle, # C1 (Red)
            self.green_candle, # C2 (Green)
            self.green_candle, # C3 (Green)
            self.green_candle, # C4 (Green)
        ]
        self.df_match = pd.DataFrame(data_match)

        # --- Data Scenario 2: Failure (one red candle) ---
        data_fail_red = [
            self.green_candle, 
            self.green_candle, 
            self.red_candle, # The failing candle
            self.green_candle,
        ]
        self.df_fail_red = pd.DataFrame(data_fail_red)

        # --- Data Scenario 3: Failure (one doji candle) ---
        data_fail_doji = [
            self.green_candle, 
            self.doji_candle, # The failing candle (Close = Open)
            self.green_candle, 
            self.green_candle,
        ]
        self.df_fail_doji = pd.DataFrame(data_fail_doji)
        
        # --- Data Scenario 4: Insufficient data ---
        data_short = [self.green_candle, self.green_candle]
        self.df_short = pd.DataFrame(data_short)
        
        # --- Data Scenario 5: Single candle test ---
        self.df_single_green = pd.DataFrame([self.green_candle])
        self.df_single_red = pd.DataFrame([self.red_candle])


    def test_successful_match(self):
        """Test case where the last N candles are all green."""
        # Check the last 3 candles in df_match: [Green, Green, Green]
        params = {N_CANDLES_LENGTH: 3, N_CANDLES_OPERATION: 1}
        result = self.indicator.evaluate(self.df_match, params)
        self.assertEqual(result, 1, "Should return 1 when last 3 candles are green")

    def test_failure_due_to_red_candle(self):
        """Test case where one of the last N candles is red."""
        # Check the last 3 in df_fail_red: [Green, Red, Green] -> Fail
        params = {N_CANDLES_LENGTH: 3, N_CANDLES_OPERATION: 1}
        result = self.indicator.evaluate(self.df_fail_red, params)
        self.assertEqual(result, 0, "Should return 0 due to a red candle in the sequence")
        
    def test_failure_due_to_doji_candle(self):
        """Test case where one of the last N candles is a doji (Close = Open)."""
        # Check the last 3 in df_fail_doji: [Doji, Green, Green] -> Fail
        params = {N_CANDLES_LENGTH: 3, N_CANDLES_OPERATION: 1}
        result = self.indicator.evaluate(self.df_fail_doji, params)
        self.assertEqual(result, 0, "Should return 0 due to a doji candle in the sequence")

    def test_insufficient_data(self):
        """Test case where data length is less than N."""
        # Data has 2 rows, N is 3 -> Fail
        params = {N_CANDLES_LENGTH: 3, N_CANDLES_OPERATION: 1}
        result = self.indicator.evaluate(self.df_short, params)
        self.assertEqual(result, 0, "Should return 0 when data length is less than n_candles")

    def test_edge_case_n_equals_data_length(self):
        """Test case where N is equal to the total data length."""
        # df_match has 4 rows, N is 4. The sequence is [Red, Green, Green, Green] -> Fail
        params = {N_CANDLES_LENGTH: 4, N_CANDLES_OPERATION: 1}
        result = self.indicator.evaluate(self.df_match, params)
        self.assertEqual(result, 0, "Should return 0 if the full history includes a red candle")

    def test_edge_case_n_equals_one(self):
        """Test case where N is 1."""
        params = {N_CANDLES_LENGTH: 1, N_CANDLES_OPERATION: 1}
        
        # Test 1: Last candle is green -> Success
        result_green = self.indicator.evaluate(self.df_single_green, params)
        self.assertEqual(result_green, 1, "Should return 1 when N=1 and the last candle is green")

        # Test 2: Last candle is red -> Fail
        result_red = self.indicator.evaluate(self.df_single_red, params)
        self.assertEqual(result_red, 0, "Should return 0 when N=1 and the last candle is red")

    def test_value_error_n_missing(self):
        """Test case for missing N_CANDLES_LENGTH parameter."""
        with self.assertRaisesRegex(ValueError, "Parameters must be provided and contain the key N_CANDLES_LENGTH"):
            self.indicator.evaluate(self.df_match, params={})

    def test_value_error_n_invalid(self):
        """Test case for non-positive or non-integer N_CANDLES_LENGTH parameter."""
        with self.assertRaisesRegex(ValueError, "N_CANDLES_LENGTH must be a positive integer."):
            self.indicator.evaluate(self.df_match, params={N_CANDLES_LENGTH: 0, N_CANDLES_OPERATION: 1})
        
        with self.assertRaisesRegex(ValueError, "N_CANDLES_LENGTH must be a positive integer."):
            self.indicator.evaluate(self.df_match, params={N_CANDLES_LENGTH: -2, N_CANDLES_OPERATION: 1})
            
        with self.assertRaisesRegex(ValueError, "N_CANDLES_LENGTH must be a positive integer."):
            self.indicator.evaluate(self.df_match, params={N_CANDLES_LENGTH: 2.5, N_CANDLES_OPERATION: 1})
            
    def test_value_error_missing_columns(self):
        """Test case for missing required columns in the DataFrame."""
        df_bad = pd.DataFrame({'Price': [100, 101], 'Volume': [1, 2]})
        params = {N_CANDLES_LENGTH: 1, N_CANDLES_OPERATION: 1}
        with self.assertRaisesRegex(ValueError, "DataFrame must contain the columns: .*"):
            self.indicator.evaluate(df_bad, params)