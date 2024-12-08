# Configuration file for backtesting and trading

# Asset and benchmark settings
SYMBOL = 'SOLUSDT'  # Asset symbol
BENCHMARK_SYMBOL = 'BTCUSDT'  # Benchmark symbol

# Backtesting settings
TIMEFRAME = '1h'  # Data granularity
INITIAL_BALANCE = 10000.0  # Starting balance in USD
FEE = 0.001  # Trading fee as a fraction (0.1%)

# Binance API credentials
API_KEY = 'yhsdzPJNebDuyxoFsHEZQ32Zuo5grZCvlqhShJilQVBvvSApe4tnVGdl94TsU32CO'
API_SECRET = 'sluOlqJuqstECUXIFQYAiXGpUA08QPGQ6jERRx1ZglSvGYE4ghwsrub3btdQcCgR'

# Strategy settings
ACTIVE_STRATEGY = 'RRS'  # Default strategy
RRS_BUY_THRESHOLD = 1.02  # Buy threshold for RRS strategy
RRS_SELL_THRESHOLD = 0.98  # Sell threshold for RRS strategy

# Performance Metrics
METRICS = {
    'calculate_duration': True,  # Duration of trades
    'calculate_exposure_time': True,  # Percentage of time with open trades
    'calculate_equity_final': True,  # Final equity value
    'calculate_equity_peak': True,  # Equity peak during backtest
    'calculate_return_percent': True,  # Total return in percentage
    'calculate_buy_and_hold_return': True,  # Return if asset was held
    'calculate_return_annual_percent': True,  # Annualized return percentage
    'calculate_volatility_annual_percent': True,  # Annualized volatility percentage
    'calculate_sharpe_ratio': True,  # Sharpe Ratio
    'calculate_sortino_ratio': True,  # Sortino Ratio
    'calculate_calmar_ratio': True,  # Calmar Ratio
    'calculate_max_drawdown_percent': True,  # Maximum drawdown percentage
    'calculate_avg_drawdown_percent': True,  # Average drawdown percentage
    'calculate_max_drawdown_duration': True,  # Max drawdown duration
    'calculate_avg_drawdown_duration': True,  # Average drawdown duration
    'calculate_trade_count': True,  # Number of trades executed
    'calculate_win_rate_percent': True,  # Winning trade percentage
    'calculate_best_trade_percent': True,  # Best trade return percentage
    'calculate_worst_trade_percent': True,  # Worst trade return percentage
    'calculate_avg_trade_percent': True,  # Average trade return percentage
    'calculate_max_trade_duration': True,  # Longest trade duration
    'calculate_avg_trade_duration': True,  # Average trade duration
}

# Additional settings
LOG_LEVEL = 'INFO'  # Logging level
