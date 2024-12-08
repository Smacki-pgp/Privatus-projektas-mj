import matplotlib.pyplot as plt
import pandas as pd

class Visualizer:
    @staticmethod
    def plot_price_and_signals(df, title="Price and Signals", save_path=None):
        """
        Plots the asset's price with buy and sell signals.

        :param df: DataFrame containing 'close' prices and 'signal' column.
        :param title: Title of the plot.
        :param save_path: Path to save the plot as an image. If None, the plot is displayed.
        """
        try:
            if df.empty:
                raise ValueError("DataFrame cannot be empty for visualization.")

            if 'close' not in df.columns or 'signal' not in df.columns:
                raise ValueError("DataFrame must contain 'close' and 'signal' columns.")

            plt.figure(figsize=(14, 7))
            plt.plot(df.index, df['close'], label="Close Price", linewidth=2, alpha=0.7)

            # Plot buy signals
            buy_signals = df[df['signal'] == 'buy']
            plt.scatter(buy_signals.index, buy_signals['close'], label="Buy Signal", marker='^', color='green', s=100, alpha=0.9)

            # Plot sell signals
            sell_signals = df[df['signal'] == 'sell']
            plt.scatter(sell_signals.index, sell_signals['close'], label="Sell Signal", marker='v', color='red', s=100, alpha=0.9)

            plt.title(title)
            plt.xlabel("Date")
            plt.ylabel("Price")
            plt.legend()
            plt.grid()

            if save_path:
                plt.savefig(save_path, dpi=300)
                print(f"Plot saved to {save_path}")
            else:
                plt.show()
        except Exception as e:
            print(f"Error in plot_price_and_signals: {e}")

    @staticmethod
    def plot_equity_curve(df, title="Equity Curve", save_path=None):
        """
        Plots the equity curve of the portfolio.

        :param df: DataFrame containing 'equity' column.
        :param title: Title of the plot.
        :param save_path: Path to save the plot as an image. If None, the plot is displayed.
        """
        try:
            if df.empty:
                raise ValueError("DataFrame cannot be empty for visualization.")

            if 'equity' not in df.columns:
                raise ValueError("DataFrame must contain 'equity' column.")

            plt.figure(figsize=(14, 7))
            plt.plot(df.index, df['equity'], label="Equity Curve", color="blue", linewidth=2, alpha=0.9)

            # Highlight equity peaks
            equity_peaks = df['equity'].cummax()
            plt.plot(df.index, equity_peaks, label="Equity Peak", color="orange", linestyle="--", linewidth=1.5, alpha=0.7)

            plt.title(title)
            plt.xlabel("Date")
            plt.ylabel("Equity")
            plt.legend()
            plt.grid()

            if save_path:
                plt.savefig(save_path, dpi=300)
                print(f"Plot saved to {save_path}")
            else:
                plt.show()
        except Exception as e:
            print(f"Error in plot_equity_curve: {e}")

if __name__ == "__main__":
    # Example data
    df = pd.DataFrame({
        'close': [100, 102, 101, 103, 105, 104, 106],
        'signal': ['hold', 'buy', 'hold', 'sell', 'hold', 'buy', 'sell'],
        'equity': [10000, 10200, 10150, 10300, 10500, 10450, 10600]
    }, index=pd.date_range(start='2023-01-01', periods=7, freq='D'))

    # Create visualizations
    Visualizer.plot_price_and_signals(df)
    Visualizer.plot_equity_curve(df)