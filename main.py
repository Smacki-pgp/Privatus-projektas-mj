import config
import data_fetcher
import data_processor
import strategy
import backtester
import metrics_calculator
import visualization

def main():
    try:
        # Step 1: Fetch data
        print("Fetching data...")
        asset_symbol = config.SYMBOL
        benchmark_symbol = config.BENCHMARK_SYMBOL
        start_date = '2023-01-01'
        end_date = '2023-12-31'

        df_asset = data_fetcher.fetch_data(asset_symbol, start_date, end_date)
        df_benchmark = data_fetcher.fetch_data(benchmark_symbol, start_date, end_date)

        if df_asset.empty or df_benchmark.empty:
            raise ValueError("Error: Could not fetch data. Ensure the symbols and date range are correct.")

        print("Asset Data:")
        print(df_asset.head())
        print("Benchmark Data:")
        print(df_benchmark.head())

        # Step 2: Process data
        print("Processing data...")
        processor = data_processor.DataProcessor(df_asset, df_benchmark)
        processed_data = processor.calculate_indicators()

        if processed_data.empty:
            raise ValueError("Error: Data processing failed. Check the input data.")

        print("Processed Data:")
        print(processed_data.head())

        # Step 3: Generate signals
        print("Generating signals...")
        strat = strategy.Strategy(config.RRS_BUY_THRESHOLD, config.RRS_SELL_THRESHOLD)
        signals = strat.generate_signals(processed_data)
        processed_data['signal'] = signals

        print("Signals:")
        print(processed_data[['signal', 'RRS']].head())

        # Step 4: Backtest strategy
        print("Backtesting strategy...")
        backtest = backtester.Backtester(processed_data, signals, config.INITIAL_BALANCE, config.FEE)
        backtest.execute_trades()

        print("Backtest Completed. Trade History:")
        print(backtest.trade_history)

        # Step 5: Calculate metrics
        print("Calculating metrics...")
        metrics_calc = metrics_calculator.MetricsCalculator(processed_data, config.INITIAL_BALANCE)
        metrics = metrics_calc.calculate_metrics()

        # Step 6: Visualize results
        print("Visualizing results...")
        visualization.Visualizer.plot_price_and_signals(processed_data, title="Price and Signals")
        visualization.Visualizer.plot_equity_curve(processed_data, title="Equity Curve")

        # Step 7: Display metrics
        print("\nBacktest Metrics:")
        for key, value in metrics.items():
            print(f"{key}: {value}")

    except ValueError as ve:
        print(f"Value Error: {ve}")
    except KeyError as ke:
        print(f"Key Error: {ke}. Check if all required columns are present in the data.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
