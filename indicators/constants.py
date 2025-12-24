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

# EMA Keys
EMA_LENGTH = 'ema_length'
DISTANCE_PCT_CAP = 'distance_pct_cap'
MIN_SLOPE_PCT = 'min_slope_pct'
EMA_HIGH = 'ema_high'
EMA_LOW = 'ema_low'

# Bollinger Bands keys
BB_LENGTH = 'bb_length'
BB_STD = 'bb_std'
BB_VARIATION_MIN = 'bb_variation_min'
BB_VARIATION_MAX = 'bb_variation_max'

# General Constants
OPERATION_TYPE = 'operation_type'
LOOKBACK = 'lookback'

# Indicators column names
CLOSE_COLUMN = 'Close'
LOW_COLUMN = 'Low'
HIGH_COLUMN = 'High'
OPEN_COLUMN = 'Open'
RSI_COLUMN = 'RSI'