import pandas as pd
import numpy as np
import logging
import os
from config import Config

# Set up logging for the data processor
log_dir = Config.OUTPUT_DIR
if log_dir and not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    filename=os.path.join(Config.OUTPUT_DIR, "data_processor.log"),
    level=logging.DEBUG if Config.DEBUG_MODE else logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"
)

def validate_columns(df, required_columns):
    """
    Validate that the DataFrame contains required columns.
    """
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

def add_moving_averages(df, short_window=10, long_window=50):
    """
    Adds moving average columns to the DataFrame.

    :param df: Input DataFrame with 'close' prices.
    :param short_window: Window size for the short moving average.
    :param long_window: Window size for the long moving average.
    :return: DataFrame with 'SMA_short' and 'SMA_long' columns added.
    """
    try:
        df[f"SMA_{short_window}"] = df['close'].rolling(window=short_window).mean()
        df[f"SMA_{long_window}"] = df['close'].rolling(window=long_window).mean()
        return df
    except Exception as e:
        logging.error(f"Error adding moving averages: {e}")
        raise

def add_rsi(df, window=14):
    """
    Adds a Relative Strength Index (RSI) column to the DataFrame.

    :param df: Input DataFrame with 'close' prices.
    :param window: Window size for calculating RSI.
    :return: DataFrame with 'RSI' column added.
    """
    try:
        delta = df['close'].diff()
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)

        avg_gain = pd.Series(gain).rolling(window=window).mean()
        avg_loss = pd.Series(loss).rolling(window=window).mean()
        
        rs = avg_gain / avg_loss
        df['RSI'] = 100 - (100 / (1 + rs))
        return df
    except Exception as e:
        logging.error(f"Error adding RSI: {e}")
        raise

def process_data(df):
    """
    Main function to process raw OHLCV data. Includes:
    - Adding moving averages
    - Adding RSI

    :param df: Input DataFrame with raw OHLCV data.
    :return: Processed DataFrame with additional technical indicators.
    """
    try:
        logging.info("Starting data processing...")
        
        # Validate required columns
        validate_columns(df, ['close'])

        # Add moving averages
        df = add_moving_averages(df, short_window=10, long_window=50)
        
        # Add RSI
        df = add_rsi(df, window=14)

        logging.info("Data processing completed successfully.")
        return df
    except Exception as e:
        logging.error(f"Error in process_data: {e}")
        raise

def save_processed_data(df, symbol):
    """
    Save the processed data to a CSV file.

    :param df: Processed DataFrame.
    :param symbol: Trading pair symbol (e.g., 'SOLUSDT').
    """
    try:
        output_file = os.path.join(Config.OUTPUT_DIR, f"{symbol}_processed_data.csv")
        df.to_csv(output_file, index=True)
        logging.info(f"Processed data saved to {output_file}.")
    except Exception as e:
        logging.error(f"Error saving processed data for {symbol}: {e}")

if __name__ == "__main__":
    try:
        # Example usage: Load raw data and process it
        input_file = os.path.join(Config.OUTPUT_DIR, f"{Config.SYMBOL}_data.csv")

        if not os.path.exists(input_file):
            logging.error(f"Input file {input_file} does not exist. Ensure `data_fetcher.py` has saved data correctly.")
        else:
            raw_data = pd.read_csv(input_file, index_col='timestamp', parse_dates=True)

            if raw_data.empty:
                logging.warning(f"Input file {input_file} is empty. No processing performed.")
            else:
                logging.info(f"Loaded raw data with {len(raw_data)} rows.")
                processed_data = process_data(raw_data)

                # Save processed data
                save_processed_data(processed_data, Config.SYMBOL)

    except Exception as e:
        logging.error(f"Error in main execution: {e}")
