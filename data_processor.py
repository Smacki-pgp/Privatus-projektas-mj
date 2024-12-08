import pandas as pd

class DataProcessor:
    def __init__(self, df_asset, df_benchmark):
        """
        Initializes the DataProcessor with asset and benchmark data.

        :param df_asset: DataFrame containing the asset's OHLCV data.
        :param df_benchmark: DataFrame containing the benchmark's OHLCV data.
        """
        self.df_asset = df_asset
        self.df_benchmark = df_benchmark

    def calculate_indicators(self):
        """
        Calculates indicators and merges asset and benchmark data.

        :return: Merged DataFrame with calculated indicators.
        """
        try:
            # Validate inputs
            if self.df_asset.empty or self.df_benchmark.empty:
                raise ValueError("Input dataframes cannot be empty.")

            # Sort dataframes by index
            self.df_asset.sort_index(inplace=True)
            self.df_benchmark.sort_index(inplace=True)

            # Ensure necessary columns exist
            required_columns = {'close'}
            if not required_columns.issubset(self.df_asset.columns):
                raise ValueError(f"Asset DataFrame is missing required columns: {required_columns - set(self.df_asset.columns)}")
            if not required_columns.issubset(self.df_benchmark.columns):
                raise ValueError(f"Benchmark DataFrame is missing required columns: {required_columns - set(self.df_benchmark.columns)}")

            # Merge the asset and benchmark data on the closest timestamps
            merged_data = pd.merge_asof(
                self.df_asset,
                self.df_benchmark,
                left_index=True,
                right_index=True,
                suffixes=('_asset', '_benchmark')
            )

            # Calculate Relative Return Strength (RRS)
            merged_data['RRS'] = merged_data['close_asset'] / merged_data['close_benchmark']

            # Debugging output
            print("Processed Data:")
            print(merged_data.head())

            return merged_data
        except Exception as e:
            print(f"Error calculating indicators: {e}")
            return pd.DataFrame()

    def normalize_data(self, df):
        """
        Normalizes data to make it suitable for strategy development.

        :param df: DataFrame to normalize.
        :return: Normalized DataFrame.
        """
        try:
            if df.empty:
                raise ValueError("Dataframe cannot be empty for normalization.")

            for column in ['open', 'high', 'low', 'close', 'volume']:
                if column in df.columns and df[column].std() != 0:
                    df[column] = (df[column] - df[column].mean()) / df[column].std()

            # Debugging output
            print("Normalized Data:")
            print(df.head())

            return df
        except Exception as e:
            print(f"Error normalizing data: {e}")
            return pd.DataFrame()

if __name__ == "__main__":
    # Example datasets
    df_asset = pd.DataFrame({
        'close': [100, 102, 101, 103, 105],
        'open': [99, 101, 100, 102, 104],
        'high': [101, 103, 102, 104, 106],
        'low': [98, 100, 99, 101, 103],
        'volume': [1000, 1500, 1200, 1300, 1600]
    }, index=pd.date_range(start='2023-01-01', periods=5, freq='D'))

    df_benchmark = pd.DataFrame({
        'close': [200, 202, 201, 203, 205],
        'open': [199, 201, 200, 202, 204],
        'high': [201, 203, 202, 204, 206],
        'low': [198, 200, 199, 201, 203],
        'volume': [2000, 2500, 2200, 2300, 2600]
    }, index=pd.date_range(start='2023-01-01', periods=5, freq='D'))

    processor = DataProcessor(df_asset, df_benchmark)
    processed_data = processor.calculate_indicators()
    normalized_data = processor.normalize_data(processed_data)

    print("Merged Data:")
    print(processed_data)
    print("\nNormalized Data:")
    print(normalized_data)
