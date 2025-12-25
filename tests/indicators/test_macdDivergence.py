import unittest
from unittest.mock import patch
import pandas as pd
from indicators.constants import (
    SIGNAL_BUY, 
    SIGNAL_SELL
)
from indicators.macdDivergence import MACDDivergence

class TestMACDDivergence(unittest.TestCase):

    @patch("pandas_ta.macd")
    def test_bullish_divergence(self, mock_macd):
        """
        Bullish Divergence: 
        Price: 90 < 100 (Lower Low)
        MACD: -1.0 > -5.0 (Higher Low)
        """
        macd_col = "MACD_12_26_9"
        slow = 26
        lookback = 5
        total_rows = slow + lookback + 5 

        # 1. Mock MACD output
        # We simulate a "trough" at index -6 and a higher "trough" at -1
        macd_values = [0.0] * total_rows
        macd_values[-(lookback + 1)] = -5.0  # Historical Low MACD
        macd_values[-1] = -1.0               # Current Higher Low MACD
        
        mock_macd.return_value = pd.DataFrame({
            macd_col: macd_values,
            "MACDs_12_26_9": [0.0] * total_rows,
            "MACDh_12_26_9": [0.0] * total_rows
        }, index=range(total_rows))

        # 2. Create Data with ALL required columns to prevent KeyError
        # Price: Historical Low 100.0, Current Low 90.0
        low_values = [110.0] * total_rows
        low_values[-(lookback + 1)] = 100.0  # Historical Low Price
        low_values[-1] = 90.0                # Current Lower Low Price

        data = pd.DataFrame({
            'Open':  [105.0] * total_rows,
            'High':  [115.0] * total_rows,
            'Low':   low_values,             # The 'Low' column for Bullish logic
            'Close': [102.0] * total_rows
        }, index=range(total_rows))

        params = {
            'fast': 12, 'slow': slow, 'signal': 9,
            'lookback': lookback, 
            'operation_type': SIGNAL_BUY
        }

        indicator = MACDDivergence(name="Div_Buy_Test", params=params)
        
        # Act
        result = indicator.evaluate(data)

        # Assert
        self.assertEqual(result, SIGNAL_BUY, f"Expected BUY ({SIGNAL_BUY}), got {result}")

    @patch("pandas_ta.macd")
    def test_bearish_divergence(self, mock_macd):
        """Bearish Divergence: Price Higher High, MACD Lower High."""
        macd_col = "MACD_12_26_9"
        slow, lookback = 26, 2
        total_rows = slow + lookback + 5 # 33 rows for plenty of padding

        # 1. Mock MACD output (29 zeros, then 5.0, then 2.0)
        macd_values = [0.0] * (total_rows - 2) + [5.0, 2.0]
        mock_macd.return_value = pd.DataFrame({
            macd_col: macd_values,
            "MACDs_12_26_9": [0.0] * total_rows,
            "MACDh_12_26_9": [0.0] * total_rows
        }, index=range(total_rows))

        # 2. Create Data with EVERY column to prevent KeyError
        # Note: We use the actual constants for the keys
        data = pd.DataFrame({
            'Open':  [100.0] * total_rows,
            'High':  [50.0] * (total_rows - 2) + [100.0, 110.0], # Highs: 100 -> 110
            'Low':   [40.0] * total_rows,                        # The missing 'Low' column
            'Close': [45.0] * (total_rows - 2) + [98.0, 108.0]
        }, index=range(total_rows))

        params = {
            'fast': 12, 'slow': slow, 'signal': 9,
            'lookback': lookback, 
            'operation_type': SIGNAL_SELL
        }

        indicator = MACDDivergence(name="Div_Sell_Test", params=params)
        
        # Act
        result = indicator.evaluate(data)

        # Assert
        self.assertEqual(result, SIGNAL_SELL, f"Expected SELL ({SIGNAL_SELL}), got {result}")