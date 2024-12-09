import pandas as pd
from binance.client import Client
import time
from config import Config
import logging
from concurrent.futures import ThreadPoolExecutor
from os import cpu_count
from binance.exceptions import BinanceAPIException
import os

# Ensure logging directory exists
log_dir = os.path.dirname(Config.LOG_FILE)
if log_dir and not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Set up logging
logging.basicConfig(
    filename=Config.LOG_FILE,
    level=logging.DEBUG if Config.DEBUG_MODE else logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"
)

client = Client(Config.API_KEY, Config.API_SECRET)

def fetch_data(symbol, start_date, end_date, interval=Config.TIMEFRAME):
    """
    Fetch historical OHLCV (Open, High, Low, Close, Volume) data for a given symbol using Binance API.

    :param symbol: Trading pair symbol (e.g., 'SOLUSDT').
    :param start_date: Start date in 'YYYY-MM-DD' format.
    :param end_date: End date in 'YYYY-MM-DD' format.
    :param interval: Data interval (e.g., '1h', '1d'). Defaults to the TIMEFRAME in Config.
    :return: DataFrame with historical OHLCV data and additional metrics.
    """
    try:
        # Ensure symbol and date parameters are valid
        if not symbol:
            raise ValueError("Symbol cannot be empty.")
        if not start_date or not end_date:
            raise ValueError("Start and end dates must be provided.")

        # Step 1: Convert input dates to timestamps in milliseconds
        start_ts = int(pd.Timestamp(start_date).timestamp() * 1000)
        end_ts = int(pd.Timestamp(end_date).timestamp() * 1000)
        logging.debug(f"Start timestamp: {start_ts}, End timestamp: {end_ts}, Symbol: {symbol}")

        all_data = []  # List to accumulate data from all API requests
        current_ts = start_ts
        iteration_limit = Config.ITERATION_LIMIT  # Limit to prevent infinite loops

        # Step 2: Determine the chunk size for fetching data
        if isinstance(Config.DATA_FETCH_CHUNK_SIZE, str):
            chunk_size = Config.DATA_FETCH_CHUNK_SIZE
            relative_mode = True  # Use Binance's relative date strings
        elif isinstance(Config.DATA_FETCH_CHUNK_SIZE, int):
            chunk_size = Config.DATA_FETCH_CHUNK_SIZE
            relative_mode = False  # Use numeric chunk sizes in milliseconds
        else:
            raise ValueError("DATA_FETCH_CHUNK_SIZE must be an integer or a valid Binance-compatible string.")

        retry_count = 0  # Counter for retry attempts
        iteration_count = 0  # Track the number of iterations

        # Step 3: Loop to fetch data in chunks until the end timestamp is reached
        while current_ts < end_ts:
            if iteration_count >= iteration_limit:
                logging.error(f"Iteration limit of {iteration_limit} reached for {symbol} after {iteration_count} iterations. Aborting to avoid infinite loop.")
                break

            iteration_count += 1

            try:
                # Fetch data using Binance API
                if relative_mode:
                    klines = client.get_historical_klines(
                        symbol, interval, f"{chunk_size} UTC", end_ts
                    )
                else:
                    klines = client.get_historical_klines(
                        symbol, interval, current_ts, min(current_ts + chunk_size, end_ts)
                    )

                # Break loop if no data is returned
                if not klines:
                    logging.warning(f"No data returned for symbol {symbol} in this time range.")
                    return pd.DataFrame()

                # Add the fetched data to the list
                all_data.extend(klines)

                # Update the current timestamp to continue fetching next chunk
                current_ts = klines[-1][0] + 1  # Move to the next available timestamp

                # Debugging: Log a sample of the fetched data
                if Config.DEBUG_MODE and klines:
                    logging.debug(f"Sample kline data for {symbol}: {klines[0]}")

                # Periodic logging for large datasets
                if len(all_data) % 1000 == 0:
                    logging.info(f"Fetched {len(all_data)} rows for {symbol} so far.")

            except BinanceAPIException as api_error:
                # Handle Binance-specific errors, including rate limits
                if api_error.code == -1003:  # Rate limit error
                    logging.error("Rate limit exceeded. Retrying after delay...")
                    time.sleep(min(60 * 2 ** retry_count, 600))  # Exponential backoff with a cap
                else:
                    logging.error(f"Binance API error: {api_error}")
                    retry_count += 1
                    if retry_count >= Config.MAX_API_RETRIES:
                        logging.error(f"Max retries reached for {symbol}. Aborting.")
                        return pd.DataFrame()
            except Exception as e:
                # Handle general errors and implement retry logic
                logging.error(f"Error during Binance API call: {e}")
                retry_count += 1
                if retry_count >= Config.MAX_API_RETRIES:
                    logging.error(f"Max retries reached for {symbol}. Aborting.")
                    return pd.DataFrame()

        # Step 4: Convert fetched data to a DataFrame for processing
        try:
            df = pd.DataFrame(all_data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])

            # Return empty DataFrame if no data was fetched
            if df.empty:
                logging.warning(f"DataFrame for symbol {symbol} is empty after fetching.")
                return df

            # Process the DataFrame: Convert timestamps and retain relevant columns
            try:
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            except Exception as e:
                logging.error(f"Error converting timestamps for {symbol}: {e}")
                return pd.DataFrame()

            df.set_index('timestamp', inplace=True)
            df = df[['open', 'high', 'low', 'close', 'volume', 'quote_asset_volume', 'number_of_trades',
                     'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume']].astype(float)

            # Add additional metrics (e.g., average price, price range, and volatility)
            df['average_price'] = (df['high'] + df['low']) / 2
            df['price_range'] = df['high'] - df['low']
            df['volatility'] = df['price_range'] / df['average_price'] * 100  # Percentage volatility

            # Debugging: Log the structure of the processed DataFrame
            if Config.DEBUG_MODE:
                logging.debug(f"Processed DataFrame for {symbol} with {len(df)} rows:\n{df.head()}")

            # Step 5: Check for missing or inconsistent data
            if df.isnull().values.any():
                logging.warning(f"DataFrame for {symbol} contains missing values. Consider handling them explicitly.")

            return df

        except Exception as e:
            logging.error(f"Error processing data for {symbol}: {e}")
            return pd.DataFrame()

    except Exception as e:
        # Log errors and return an empty DataFrame in case of failure
        logging.error(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()

def fetch_multiple_symbols(symbols, start_date, end_date):
    """
    Fetch data for multiple symbols concurrently.

    :param symbols: List of symbols to fetch data for.
    :param start_date: Start date for all symbols.
    :param end_date: End date for all symbols.
    :return: Dictionary of DataFrames indexed by symbol.
    """
    # Determine the number of threads to use for concurrent fetching
    max_workers = Config.MAX_WORKERS if Config.USE_MULTITHREADING else 1
    results = {}

    # Use ThreadPoolExecutor to fetch data concurrently
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(fetch_data, symbol, start_date, end_date): symbol
            for symbol in symbols
        }

        for future in futures:
            symbol = futures[future]
            logging.info(f"Starting data fetch for {symbol} from {start_date} to {end_date}.")  # Log the start of fetching with time range
            try:
                result = future.result()
                if result.empty:
                    logging.warning(f"No data fetched for {symbol}.")
                else:
                    results[symbol] = result
                    # Debugging: Validate fetched data
                    if Config.DEBUG_MODE:
                        logging.debug(f"Data fetched for {symbol}: {len(result)} rows.")
            except Exception as e:
                # Log errors encountered during concurrent fetching
                logging.error(f"Error fetching data for {symbol}: {e}")
    return results

if __name__ == "__main__":
    # Example configuration for testing
    symbols = [Config.SYMBOL, Config.BENCHMARK_SYMBOL]
    start_date = "2023-01-01"
    end_date = "2023-01-10"  # Adjusted to fetch more timestamps

    print("Fetching data for symbols...")
    data = fetch_multiple_symbols(symbols, start_date, end_date)

    # Step 7: Validate output and save to CSV
    for symbol, df in data.items():
        if not df.empty:
            print(f"Fetched data for {symbol}: {len(df)} rows.")
            df.to_csv(f"{symbol}_data.csv", index=True)
            logging.info(f"Saved {symbol} data to {symbol}_data.csv.")
        else:
            logging.warning(f"No data fetched for {symbol}.")
