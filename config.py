import logging
import os

class Config:
    """
    Configuration settings for the trading system.
    Adjust these parameters based on your environment and preferences.
    """

    # Binance API Credentials (Set these securely via environment variables)
    API_KEY = os.getenv("BINANCE_API_KEY", "yhsdzPJNebDuyxoFsHEZQ32Zuo5grZCvlqhShJilQVBvvSApe4tnVGdl94TsU32CO")
    API_SECRET = os.getenv("BINANCE_API_SECRET", "sluOlqJuqstECUXIFQYAiXGpUA08QPGQ6jERRx1ZglSvGYE4ghwsrub3btdQcCgR")

    # Logging Configuration
    LOG_FILE = "trading_system.log"  # Path to the log file
    DEBUG_MODE = True  # Set to False for production to reduce log verbosity

    # Data Fetching Parameters
    TIMEFRAME = "1h"  # Time interval for data fetching (e.g., '1h', '1d')
    START_DATE = "2023-01-01"  # Start date for historical data fetching (YYYY-MM-DD)
    END_DATE = "2023-12-31"  # End date for historical data fetching (YYYY-MM-DD)
    DATA_FETCH_CHUNK_SIZE = 1000  # Max data points per API call (int or Binance-compatible string)
    MAX_API_RETRIES = 5  # Number of retries for API errors
    USE_MULTITHREADING = True  # Use multithreading to fetch data for multiple symbols concurrently
    MAX_WORKERS = 4  # Number of threads for concurrent fetching
    ITERATION_LIMIT = 1000  # Limit the number of iterations during data fetching

    # Symbols and Benchmarks
    SYMBOL = "SOLUSDT"  # Primary trading pair
    BENCHMARK_SYMBOL = "BTCUSDT"  # Benchmark trading pair for comparison

    # Backtesting Parameters
    INITIAL_BALANCE = 10000.0  # Starting portfolio balance in USD
    TRADING_FEES = 0.001  # Trading fee as a percentage (e.g., 0.1% = 0.001)

    # Strategy Parameters
    ACTIVE_STRATEGY = "RRS"  # Current active strategy (e.g., 'RRS')
    RRS_BUY_THRESHOLD = 1.02  # RRS threshold to trigger a buy signal
    RRS_SELL_THRESHOLD = 0.98  # RRS threshold to trigger a sell signal

    # Output Settings
    OUTPUT_DIRECTORY = "data_output"  # Directory to save output CSVs and results

    # Metrics Configuration (For detailed backtesting analytics)
    METRICS_TO_CALCULATE = [
        "Duration",
        "Exposure Time %",
        "Equity Final",
        "Equity Peak",
        "Return %",
        "Buy and Hold Return %",
        "Return Annual %",
        "Volatility Annual %",
        "Sharpe Ratio",
        "Sortino Ratio",
        "Calmar Ratio",
        "Max Drawdown %",
        "Avg Drawdown %",
        "Max Drawdown Duration",
        "Avg Drawdown Duration",
        "# Trades",
        "Win Rate %",
        "Best Trade %",
        "Worst Trade %",
        "Avg. Trade %",
        "Max Trade Duration",
        "Avg Trade Duration",
    ]

    @staticmethod
    def validate():
        """
        Validate essential configurations to ensure correctness before execution.
        """
        if not Config.API_KEY:
            logging.error("API_KEY is not set. Ensure you set it via environment variables or directly in the config.")
        if not Config.API_SECRET:
            logging.error("API_SECRET is not set. Ensure you set it via environment variables or directly in the config.")

        assert Config.TIMEFRAME in ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "1d"], (
            f"Invalid TIMEFRAME: {Config.TIMEFRAME}. Choose a valid Binance interval."
        )
        assert isinstance(Config.DATA_FETCH_CHUNK_SIZE, (int, str)), (
            "DATA_FETCH_CHUNK_SIZE must be an integer or a Binance-compatible string."
        )
        assert Config.SYMBOL, "SYMBOL must be defined."
        assert Config.BENCHMARK_SYMBOL, "BENCHMARK_SYMBOL must be defined."

        # Create output directory if it doesn't exist
        if not os.path.exists(Config.OUTPUT_DIRECTORY):
            try:
                os.makedirs(Config.OUTPUT_DIRECTORY)
            except OSError as e:
                logging.error(f"Failed to create output directory {Config.OUTPUT_DIRECTORY}: {e}")
                raise

        logging.info("Configuration validation successful.")

# Execute validation on import
try:
    Config.validate()
except AssertionError as e:
    logging.error(f"Configuration validation failed: {e}")
    raise
