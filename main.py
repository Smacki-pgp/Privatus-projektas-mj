import config
from data_fetcher import DataFetcher
from data_processor import DataProcessor
from strategy import Strategy
from backtester import Backtester
from visualizer import Visualizer

def run_bot():
    df_asset = DataFetcher(config.SYMBOL, config.TIMEFRAME).fetch_data()
    print("Fetched asset data:")
    print(df_asset.head())

    df_benchmark = DataFetcher(config.BENCHMARK_SYMBOL, config.TIMEFRAME).fetch_data()
    print("Fetched benchmark data:")
    print(df_benchmark.head())

    processed_data = DataProcessor(df_asset, df_benchmark).calculate_indicators()
    print("Processed data with RRS:")
    print(processed_data.head())

    signals = Strategy(processed_data, config.ACTIVE_STRATEGY).generate_signals()
    print("Generated signals:")
    print(signals.head())

    backtest_results = Backtester(processed_data, signals).run_backtest()
    Visualizer(processed_data, signals, backtest_results).plot()

if __name__ == "__main__":
    run_bot()