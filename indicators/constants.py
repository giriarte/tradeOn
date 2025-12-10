# indicators/constants.py

import typing as t

# --- SIGNAL CONSTANTS ---
SIGNAL_HOLD = 0
SIGNAL_BUY = 1
SIGNAL_SELL = 2

# RSI Keys
RSI_LENGTH = 'rsi_length'
RSI_BUY_THRESHOLD = 'rsi_buy_threshold'
RSI_SELL_THRESHOLD = 'rsi_sell_threshold'

# N-Candles Keys
N_CANDLES_LENGTH = 'n_candles_length'
N_CANDLES_OPERATION = 'n_candles_operation'
N_CANDLES_OFFSET = 'n_candles_offset'

# Indicators column names
CLOSE_COLUMN = 'Close'
OPEN_COLUMN = 'Open'
RSI_COLUMN = 'RSI'