import pandas as pd
from binance.client import Client
import config

def fetch_data(symbol, start_date, end_date, interval='1h'):
    """
    Fetch historical data for a given symbol using Binance API.

    :param symbol: Trading pair symbol (e.g., 'SOLUSDT').
    :param start_date: Start date in 'YYYY-MM-DD' format.
    :param end_date: End date in 'YYYY-MM-DD' format.
    :param interval: Data interval (e.g., '1h', '1d').
    :return: DataFrame with historical OHLCV data.
    """
    try:
        # Validate inputs
        if not symbol:
            raise ValueError("Symbol cannot be empty.")
        if not start_date or not end_date:
            raise ValueError("Start date and end date must be provided.")

        client = Client(config.API_KEY, config.API_SECRET)

        # Convert dates to milliseconds
        start_ts = int(pd.Timestamp(start_date).timestamp() * 1000)
        end_ts = int(pd.Timestamp(end_date).timestamp() * 1000)

        # Fetch klines
        klines = client.get_historical_klines(symbol, interval, start_ts, end_ts)

        if not klines:
            raise ValueError(f"No data fetched for {symbol} from {start_date} to {end_date}.")

        # Create DataFrame
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])

        # Process and standardize DataFrame
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)

        # Debugging output
        print("Fetched Data:")
        print(df.head())

        return df

    except ValueError as ve:
        print(f"Input error: {ve}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    # Example configuration for testing
    symbol = config.SYMBOL  # e.g., 'SOLUSDT'
    start_date = '2023-01-01'
    end_date = '2023-12-31'

    # Fetch and display data
    data = fetch_data(symbol, start_date, end_date)
    if not data.empty:
        print(data.head())
    else:
        print("No data fetched.")