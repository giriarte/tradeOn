import unittest
import pandas as pd
from unittest import mock
import typing as t
from indicators.rsi import RSI

# 2. Mock the pandas_ta library import
class MockTA:
    @staticmethod
    def rsi(series, length):
        # We replace this function with a mock object in the test
        return pd.Series([None] * (length - 1) + [50.0] * 5) # Default mock return

# ----------------------------------------------------------------------
# UNIT TEST CLASS
# ----------------------------------------------------------------------

# We use @mock.patch to replace the external pandas_ta.rsi function 
# with our own controlled function for the duration of the test run.
# Replace 'your_module_name.ta.rsi' with the correct import path if needed.

# Since we mocked the whole class in the test file, we don't need the patch decorator.
# We will control the RSI series returned inside the setUp method.

class TestRSIIndicator(unittest.TestCase):
    
    def setUp(self):
        self.indicator = RSI()
        
        # Create a mock DataFrame that is long enough (100 rows)
        self.df_base = pd.DataFrame({'Close': [i + 100 for i in range(100)]})
        
    # We patch the RSI calculation call for each test case below
    # We will patch the MockTA.rsi function defined above to control the output
    
    @mock.patch('indicators.rsi.ta.rsi')
    def test_buy_signal(self, mock_rsi):
        """Tests the Buy signal condition (RSI <= Buy Threshold)."""
        # 1. Setup mock RSI to return 25 (Oversold)
        mock_rsi.return_value = pd.Series([25.0] * len(self.df_base))
        
        # 2. Define parameters: Buy @ 30, Sell @ 70
        params = {'length': 14, 'buy_threshold': 30, 'sell_threshold': 70}
        
        # 3. Evaluate
        result = self.indicator.evaluate(self.df_base, params)
        
        # 4. Assert
        self.assertEqual(result, 1, "Should return 1 (Buy) when RSI is 25 <= 30")

    @mock.patch('indicators.rsi.ta.rsi')
    def test_sell_signal(self, mock_rsi):
        """Tests the Sell signal condition (RSI >= Sell Threshold)."""
        # 1. Setup mock RSI to return 75 (Overbought)
        mock_rsi.return_value = pd.Series([75.0] * len(self.df_base))
        
        # 2. Define parameters: Buy @ 30, Sell @ 70
        params = {'length': 14, 'buy_threshold': 30, 'sell_threshold': 70}
        
        # 3. Evaluate
        result = self.indicator.evaluate(self.df_base, params)
        
        # 4. Assert
        self.assertEqual(result, 2, "Should return 2 (Sell) when RSI is 75 >= 70")

    @mock.patch('indicators.rsi.ta.rsi')
    def test_hold_signal(self, mock_rsi):
        """Tests the Hold signal condition (RSI is between thresholds)."""
        # 1. Setup mock RSI to return 50
        mock_rsi.return_value = pd.Series([50.0] * len(self.df_base))
        
        # 2. Define parameters: Buy @ 30, Sell @ 70
        params = {'length': 14, 'buy_threshold': 30, 'sell_threshold': 70}
        
        # 3. Evaluate
        result = self.indicator.evaluate(self.df_base, params)
        
        # 4. Assert
        self.assertEqual(result, 0, "Should return 0 (Hold) when RSI is 50")

    @mock.patch('indicators.rsi.ta.rsi')
    def test_default_parameters(self, mock_rsi):
        """Tests execution using the default thresholds (30/70) and length (10)."""
        # 1. Setup mock RSI to return 28
        mock_rsi.return_value = pd.Series([28.0] * len(self.df_base))
        
        # 2. Evaluate with empty params (uses defaults)
        result = self.indicator.evaluate(self.df_base, params={})
        
        # 3. Assert (28 <= default 30, so Buy)
        self.assertEqual(result, 1, "Should return 1 (Buy) using default params (RSI 28 <= 30)")


    def test_insufficient_data(self):
        """Tests when the final RSI value is NaN/None."""
        # We manually create a DataFrame that is too short for any RSI calculation
        df_short = pd.DataFrame({'Close': [100, 101, 102]})
        
        # No need to mock ta.rsi, the method logic should catch the failure
        # (Assuming the actual ta.rsi returns NaN for insufficient length)
        
        # Evaluate with length=10
        result = self.indicator.evaluate(df_short, params={'length': 10})
        
        self.assertEqual(result, 0, "Should return 0 when RSI calculation fails due to insufficient data")
        
    def test_missing_close_column(self):
        """Tests DataFrame missing the required 'Close' column."""
        # Data without