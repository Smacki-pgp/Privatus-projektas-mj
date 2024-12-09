import pandas as pd
from binance.client import Client
import asyncio
import os
import logging
from config import Config
from binance.exceptions import BinanceAPIException
from datetime import time
# Ensure logging directory exists
log_dir = os.path.dirname(Config.LOG_FILE)
if log_dir and not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Set up logging
logging.basicConfig(
    filename=Config.LOG_FILE,
    level=logging.DEBUG,  # Keep detailed logs even in production mode
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"
)

# Add console logging
console = logging.StreamHandler()
console.setLevel(logging.DEBUG if Config.DEBUG_MODE else logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

# Initialize Binance client
client = Client(Config.API_KEY, Config.API_SECRET)

# Ensure output directory exists
if not os.path.exists(Config.OUTPUT_DIR):
    os.makedirs(Config.OUTPUT_DIR, exist_ok=True)

# Function to validate trading pair and interval
# Ensures that the given symbol and interval are supported by the Binance API
def validate_symbol_and_interval(symbol, interval):
    """
    Validate the symbol and interval against Binance API supported values.

    :param symbol: Trading pair symbol (e.g., 'SOLUSDT').
    :param interval: Data interval (e.g., '1h').
    :raises ValueError: If validation fails.
    """
    try:
        info = client.get_exchange_info()
        valid_symbols = {s['symbol'] for s in info['symbols']}
        valid_intervals = [
            '1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h',
            '6h', '8h', '12h', '1d', '3d', '1w', '1M'
        ]

        if symbol not in valid_symbols:
            raise ValueError(f"Invalid symbol: {symbol}. Ensure it exists on Binance.")
        if interval not in valid_intervals:
            raise ValueError(f"Invalid interval: {interval}. Supported intervals: {valid_intervals}")
    except Exception as e:
        logging.error(f"Error validating symbol and interval: {e}")
        raise

# Function to save fetched data to a CSV file
# Saves the DataFrame to the output directory defined in the configuration
def save_data_to_csv(df, symbol):
    try:
        output_file = os.path.join(Config.OUTPUT_DIR, f"{symbol}_data.csv")
        logging.debug(f"Attempting to save data to {output_file}. DataFrame size: {df.shape}")
        
        if df.empty:
            logging.warning(f"No data to save for {symbol}. Skipping CSV write.")
            return
        
        df.to_csv(output_file, index=True)
        logging.info(f"Data for {symbol} successfully saved to {output_file}.")
    except Exception as e:
        logging.error(f"Error saving data for {symbol}: {e}", exc_info=True)

# Function to fetch historical OHLCV data asynchronously
# Retrieves data in chunks to avoid exceeding API limits
async def fetch_data_async(symbol, start_date, end_date, interval=Config.TIMEFRAME, max_retries=3):
    """
    Fetch historical OHLCV data asynchronously with enhanced error handling and retries.

    :param symbol: Trading pair symbol (e.g., 'SOLUSDT').
    :param start_date: Start date for data (e.g., '2023-01-01').
    :param end_date: End date for data (e.g., '2023-02-01').
    :param interval: Data interval (e.g., '1h'). Defaults to Config.TIMEFRAME.
    :param max_retries: Maximum number of retries for transient errors.
    :return: DataFrame containing the fetched data.
    """
    try:
        validate_symbol_and_interval(symbol, interval)
        logging.debug(f"Validation passed for symbol: {symbol}, interval: {interval}")

        start_ts = int(pd.Timestamp(start_date).timestamp() * 1000)
        end_ts = int(pd.Timestamp(end_date).timestamp() * 1000)
        all_data = []
        current_ts = start_ts

        logging.info(f"Fetching data for {symbol} from {start_date} to {end_date} with interval {interval}")

        while current_ts < end_ts:
            retries = 0
            while retries <= max_retries:
                try:
                    logging.debug(f"Fetching chunk from {current_ts} to {min(current_ts + Config.DATA_FETCH_CHUNK_SIZE, end_ts)} for {symbol}")
                    klines = client.get_historical_klines(
                        symbol, interval, current_ts, min(current_ts + Config.DATA_FETCH_CHUNK_SIZE, end_ts)
                    )

                    if not klines:
                        logging.warning(f"No data returned for {symbol} in chunk {current_ts} to {end_ts}. Stopping fetch.")
                        break

                    all_data.extend(klines)
                    current_ts = klines[-1][0] + 1
                    logging.info(f"Fetched {len(klines)} rows for {symbol} in current chunk.")

                    if len(all_data) % 1000 == 0:
                        logging.info(f"Fetched {len(all_data)} total rows for {symbol} so far.")
                    break  # Exit retry loop on success

                except BinanceAPIException as api_error:
                    if api_error.code == -1003:  # Rate limit exceeded
                        logging.warning("Rate limit exceeded. Retrying after 60 seconds...")
                        await asyncio.sleep(60)
                    else:
                        logging.error(f"Binance API error for {symbol}: {api_error}")
                        raise  # Re-raise non-rate-limit errors

                except Exception as e:
                    retries += 1
                    logging.error(f"Error fetching data chunk for {symbol}: {e}. Retrying ({retries}/{max_retries})...")
                    if retries > max_retries:
                        logging.error(f"Max retries exceeded for chunk starting at {current_ts}. Skipping...")
                        current_ts += Config.DATA_FETCH_CHUNK_SIZE  # Skip problematic chunk
                        break

        if not all_data:
            logging.warning(f"No data fetched for {symbol}. Returning empty DataFrame.")
            return pd.DataFrame()

        # Convert data to DataFrame
        df = pd.DataFrame(all_data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
        
        logging.info(f"Data successfully fetched and converted to DataFrame for {symbol}.")
        return df

    except Exception as e:
        logging.error(f"Error in fetch_data_async for {symbol}: {e}", exc_info=True)
        return pd.DataFrame()


# Function to fetch data for multiple symbols concurrently
# Executes the asynchronous fetch function for each symbol
async def fetch_multiple_symbols_async(symbols, start_date, end_date):
    """
    Fetch data for multiple symbols concurrently.

    :param symbols: List of trading pair symbols.
    :param start_date: Start date for data (e.g., '2023-01-01').
    :param end_date: End date for data (e.g., '2023-02-01').
    :return: Dictionary with symbols as keys and DataFrames as values.
    """
    logging.info(f"Preparing to fetch data for symbols: {symbols}")
    
    tasks = []
    for symbol in symbols:
        logging.debug(f"Creating task for symbol: {symbol}")
        tasks.append(fetch_data_async(symbol, start_date, end_date))
    
    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        logging.debug(f"Data fetch completed for all symbols.")
        
        data = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, Exception):
                logging.error(f"Error fetching data for {symbol}: {result}")
                data[symbol] = pd.DataFrame()  # Return empty DataFrame on error
            else:
                data[symbol] = result
        
        return data

    except Exception as e:
        logging.error(f"Unexpected error during multiple symbol data fetch: {e}", exc_info=True)
        return {}

if __name__ == "__main__":
    # Main script to initiate data fetch
    # Fetches data for the configured symbols and saves the results to CSV files
    symbols = [Config.SYMBOL, Config.BENCHMARK_SYMBOL]
    start_date = Config.START_DATE
    end_date = Config.END_DATE

    logging.info("Starting data fetch...")
    print("Fetching data for symbols...")

    try:
        logging.info("Starting data fetching for multiple symbols...")
        data = asyncio.run(fetch_multiple_symbols_async(symbols, start_date, end_date))
    
        for symbol, df in data.items():
            if df is not None and not df.empty:
                logging.info(f"Fetched {len(df)} rows for {symbol}.")
                save_data_to_csv(df, symbol)
            else:
                logging.warning(f"No data fetched for {symbol}.")
    except Exception as e:
        logging.error(f"Error during data fetching or saving: {e}", exc_info=True)
