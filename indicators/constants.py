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
STOCH_LENGTH = 'stoch_length'
K_PERIOD = 'k_period'
D_PERIOD = 'd_period'
THRESHOLD = 'threshold'

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

# ADX Keys
ADX_LENGTH = 'adx_length'
ADX_MIN = 'adx_min'
ADX_MAX = 'adx_max'
DMP_MIN = 'dmp_min'
DMP_MAX = 'dmp_max'
DMN_MIN = 'dmn_min'
DMN_MAX = 'dmn_max'

# Bollinger Bands keys
BB_LENGTH = 'bb_length'
BB_STD = 'bb_std'
BB_VARIATION_MIN = 'bb_variation_min'
BB_VARIATION_MAX = 'bb_variation_max'

# MACD Keys
MACD_FAST = 'macd_fast'
MACD_SLOW = 'macd_slow'
MACD_SIGNAL = 'macd_signal'

# General Constants
OPERATION_TYPE = 'operation_type'
LOOKBACK = 'lookback'
TARGET_LEVEL = 'target_level'
TOLERANCE_PCT = 'tolerance_pct'
RESISTANCE_LOOKBACK = 'resistance_lookback'
SUPPORT_LOOKBACK = 'support_lookback'

# Indicators column names
CLOSE_COLUMN = 'Close'
LOW_COLUMN = 'Low'
HIGH_COLUMN = 'High'
OPEN_COLUMN = 'Open'
RSI_COLUMN = 'RSI'