import matplotlib.pyplot as plt

class Visualizer:
    def __init__(self, df, signals, backtest_results):
        self.df = df
        self.signals = signals
        self.backtest_results = backtest_results

    def plot(self):
        fig, ax1 = plt.subplots(figsize=(14, 7))

        # Plot RRS values
        ax1.plot(self.df['timestamp'], self.df['RRS'], label='Relative Strength (RRS)', color='blue')
        ax1.set_xlabel('Timestamp')
        ax1.set_ylabel('RRS', color='blue')
        ax1.legend(loc='upper left')

        # Highlight Buy/Sell signals
        buy_signals = self.signals[self.signals['signal'] == 'buy']
        sell_signals = self.signals[self.signals['signal'] == 'sell']

        ax1.scatter(buy_signals.index, buy_signals['RRS'], label='Buy Signal', color='green', marker='^')
        ax1.scatter(sell_signals.index, sell_signals['RRS'], label='Sell Signal', color='red', marker='v')

        # Plot balance
        ax2 = ax1.twinx()
        ax2.plot(self.df['timestamp'], self.df['close'].cumsum(), label='Cumulative Returns', color='orange')
        ax2.set_ylabel('Cumulative Returns', color='orange')
        ax2.legend(loc='upper right')

        plt.title('Backtest Results')
        plt.show()
