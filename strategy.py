import pandas as pd
import config
class Strategy:
    def __init__(self, df, strategy_name):
        self.df = df
        self.strategy_name = strategy_name

    def generate_signals(self):
        if self.strategy_name == 'RRS':
            signals = pd.Series(index=self.df.index)
            # Generate buy signal when RRS crosses above the buy threshold
            signals[self.df['RRS'] > config.RRS_BUY_THRESHOLD] = 'buy'
            # Generate sell signal when RRS crosses below the sell threshold
            signals[self.df['RRS'] < config.RRS_SELL_THRESHOLD] = 'sell'
            return signals
        else:
            raise ValueError("Unsupported strategy name")