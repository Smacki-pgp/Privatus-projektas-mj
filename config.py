# Configurations for Binance API and Data Fetching

class Config:
    # Binance API keys (replace with your own keys)
    API_KEY = "yhsdzPJNebDuyxoFsHEZQ32Zuo5grZCvlqhShJilQVBvvSApe4tnVGdl94TsU32CO"
    API_SECRET = "sluOlqJuqstECUXIFQYAiXGpUA08QPGQ6jERRx1ZglSvGYE4ghwsrub3btdQcCgR"

    # Logging configuration
    LOG_FILE = "logs/data_fetcher.log"
    DEBUG_MODE = False  # Set to False in production

    # Default trading pairs and time settings
    SYMBOL = "SOLUSDT"  # Main symbol to fetch data for
    BENCHMARK_SYMBOL = "BTCUSDT"  # Secondary symbol for comparisons
    START_DATE = "2023-01-01"  # Start date for historical data
    END_DATE = "2023-02-06"  # End date for historical data
    TIMEFRAME = "1h"  # Data interval

    # Data fetching configuration
    DATA_FETCH_CHUNK_SIZE = 60 * 60 * 1000  # Chunk size in milliseconds (default 1 hour per fetch)
    MAX_API_RETRIES = 5  # Max retries for API calls

    # Multithreading and rate limit handling
    MAX_CONCURRENT_REQUESTS = 10  # Maximum concurrent API calls
    RATE_LIMIT_CHECK_INTERVAL = 60  # Interval in seconds to check rate limits

    # CSV Output
    SAVE_CSV = True  # Set to False if you don't want to save fetched data as CSV
    OUTPUT_DIR = "output/"  # Directory to save CSV files

    # Advanced configurations
    USE_WEBSOCKETS = False  # Enable WebSocket support for live data
    RATE_LIMIT_WARNING_THRESHOLD = 80  # Percentage of rate limit usage to trigger warnings
    DATABASE_ENABLED = False  # If True, save data to a database instead of CSV
    DATABASE_URI = "sqlite:///data_fetcher.db"  # Database connection URI (e.g., SQLite, PostgreSQL)

    # Derived settings
    @staticmethod
    def create_directories():
        """
        Create necessary directories for logs and output.
        """
        import os
        try:
        # Ensure directories exist for logs and output
            if not os.path.exists(os.path.dirname(Config.LOG_FILE)):
                os.makedirs(os.path.dirname(Config.LOG_FILE), exist_ok=True)
            if Config.SAVE_CSV and not os.path.exists(Config.OUTPUT_DIR):
                os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
        except Exception as e:
            raise RuntimeError(f"Error creating directories: {e}")

    @staticmethod
    def validate_api_keys():
        """
        Validate that API keys are provided.
        """
        if not Config.API_KEY or not Config.API_SECRET:
            raise ValueError("API_KEY and API_SECRET must be set in the configuration.")

    @staticmethod
    def validate_timeframe():
        """
        Validate the specified timeframe is supported by Binance.
        """
        valid_intervals = [
            '1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h',
            '6h', '8h', '12h', '1d', '3d', '1w', '1M'
        ]
        if Config.TIMEFRAME not in valid_intervals:
            raise ValueError(f"Invalid TIMEFRAME: {Config.TIMEFRAME}. Supported intervals: {valid_intervals}")

    @staticmethod
    def validate_date_range():
        """
        Validate the date range to ensure the start date is earlier than the end date.
        """
        from datetime import datetime
        try:
            start_date = datetime.strptime(Config.START_DATE, "%Y-%m-%d")
            end_date = datetime.strptime(Config.END_DATE, "%Y-%m-%d")
            if start_date >= end_date:
                raise ValueError("START_DATE must be earlier than END_DATE.")
        except Exception as e:
            raise ValueError(f"Invalid date range: {e}")

# Ensure necessary directories are created and configurations are validated
Config.create_directories()
Config.validate_api_keys()
Config.validate_timeframe()
Config.validate_date_range()
