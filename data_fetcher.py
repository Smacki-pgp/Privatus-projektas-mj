import pandas as pd
from binance.client import Client
import time
from config import Config
import logging
import asyncio
import os
from binance.exceptions import BinanceAPIException

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

def validate_symbol_and_interval(symbol, interval):
    """
    Validate the symbol and interval against Binance API supported values.

    :param symbol: Trading pair symbol (e.g., 'SOLUSDT').
    :param interval: Interval to validate (e.g., '1h').
    :raises ValueError: If the symbol or interval is invalid.
    """
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

def get_market_depth(symbol):
    """
    Fetch order book depth for a symbol.

    :param symbol: Trading pair symbol (e.g., 'SOLUSDT').
    :return: Dictionary containing bid and ask data.
    """
    try:
        depth = client.get_order_book(symbol=symbol)
        return {
            'bids': depth['bids'],
            'asks': depth['asks']
        }
    except BinanceAPIException as e:
        logging.error(f"Error fetching market depth for {symbol}: {e}")
        return {}

def fetch_real_time_price(symbol):
    """
    Fetch the current real-time price of a symbol.

    :param symbol: Trading pair symbol (e.g., 'SOLUSDT').
    :return: Current price of the symbol.
    """
    try:
        ticker = client.get_symbol_ticker(symbol=symbol)
        return float(ticker['price'])
    except BinanceAPIException as e:
        logging.error(f"Error fetching real-time price for {symbol}: {e}")
        return None

async def fetch_data_async(symbol, start_date, end_date, interval=Config.TIMEFRAME):
    """
    Fetch historical OHLCV (Open, High, Low, Close, Volume) data for a given symbol using Binance API asynchronously.

    :param symbol: Trading pair symbol (e.g., 'SOLUSDT').
    :param start_date: Start date in 'YYYY-MM-DD' format.
    :param end_date: End date in 'YYYY-MM-DD' format.
    :param interval: Data interval (e.g., '1h', '1d'). Defaults to the TIMEFRAME in Config.
    :return: DataFrame with historical OHLCV data and additional metrics.
    """
    try:
        validate_symbol_and_interval(symbol, interval)

        start_ts = int(pd.Timestamp(start_date).timestamp() * 1000)
        end_ts = int(pd.Timestamp(end_date).timestamp() * 1000)
        logging.debug(f"Fetching {symbol} from {pd.to_datetime(start_ts, unit='ms')} to {pd.to_datetime(end_ts, unit='ms')}.")

        all_data = []
        current_ts = start_ts
        retry_count = 0

        while current_ts < end_ts:
            try:
                klines = client.get_historical_klines(
                    symbol, interval, current_ts, min(current_ts + Config.DATA_FETCH_CHUNK_SIZE, end_ts)
                )

                if not klines:
                    logging.warning(f"No data returned for {symbol} between {start_date} and {end_date}. Reducing time range and retrying.")
                    # Adjust the range to fetch smaller chunks
                    end_ts = current_ts + Config.DATA_FETCH_CHUNK_SIZE // 2
                    continue

                all_data.extend(klines)
                current_ts = klines[-1][0] + 1

                if Config.DEBUG_MODE and klines:
                    logging.debug(f"Sample data for {symbol}: {klines[0]}")

                if len(all_data) % 1000 == 0:
                    logging.info(f"Fetched {len(all_data)} rows for {symbol} so far.")

            except BinanceAPIException as api_error:
                if api_error.code == -1003:
                    logging.error("Rate limit exceeded. Retrying...")
                    await asyncio.sleep(min(60 * 2 ** retry_count, 600))
                    retry_count += 1
                else:
                    logging.error(f"Binance API error for {symbol}: {api_error}")
                    break

            except Exception as e:
                logging.error(f"Error during API call for {symbol}: {e}")
                retry_count += 1
                if retry_count >= Config.MAX_API_RETRIES:
                    logging.error(f"Max retries reached for {symbol}. Aborting.")
                    break

        df = pd.DataFrame(all_data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])

        if df.empty:
            logging.warning(f"DataFrame for {symbol} is empty after fetching.")
            return df

        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        df = df[['open', 'high', 'low', 'close', 'volume', 'quote_asset_volume', 'number_of_trades',
                 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume']].astype(float)

        df['average_price'] = (df['high'] + df['low']) / 2
        df['price_range'] = df['high'] - df['low']
        df['volatility'] = df['price_range'] / df['average_price'] * 100

        if Config.DEBUG_MODE:
            logging.debug(f"Processed DataFrame for {symbol} with {len(df)} rows:\n{df.head()}")

        return df

    except Exception as e:
        logging.error(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()

async def fetch_multiple_symbols_async(symbols, start_date, end_date):
    """
    Fetch data for multiple symbols concurrently using asyncio.

    :param symbols: List of symbols to fetch data for.
    :param start_date: Start date for all symbols.
    :param end_date: End date for all symbols.
    :return: Dictionary of DataFrames indexed by symbol.
    """
    tasks = [fetch_data_async(symbol, start_date, end_date) for symbol in symbols]
    results = await asyncio.gather(*tasks)

    return {symbol: result for symbol, result in zip(symbols, results)}

def check_rate_limit():
    """
    Monitor the API rate limit usage using the `X-MBX-USED-WEIGHT` header.
    """
    headers = client.response.headers
    rate_limit_used = headers.get("X-MBX-USED-WEIGHT-1M", None)
    if rate_limit_used:
        logging.info(f"Current rate limit usage: {rate_limit_used}")

if __name__ == "__main__":
    symbols = [Config.SYMBOL, Config.BENCHMARK_SYMBOL]
    start_date = Config.START_DATE
    end_date = Config.END_DATE

    print("Fetching data for symbols...")
    data = asyncio.run(fetch_multiple_symbols_async(symbols, start_date, end_date))

    for symbol, df in data.items():
        if not df.empty:
            print(f"Fetched data for {symbol}: {len(df)} rows.")
            df.to_csv(f"{symbol}_data.csv", index=True)
            logging.info(f"Saved data for {symbol} to {symbol}_data.csv.")
        else:
            logging.warning(f"No data fetched for {symbol}.")