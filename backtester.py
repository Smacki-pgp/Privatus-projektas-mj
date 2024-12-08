import pandas as pd
import config

class Backtester:
    def __init__(self, df, signals):
        """
        Initializes the Backtester with data, signals, and initial configuration.

        :param df: DataFrame containing price data and signals.
        :param signals: Series containing buy/sell signals.
        """
        self.df = df
        self.signals = signals
        self.initial_balance = config.INITIAL_BALANCE
        self.fee = config.FEE
        self.balance = self.initial_balance
        self.positions = []
        self.trade_history = []

    def execute_trades(self):
        """
        Simulates trade execution based on signals.
        """
        try:
            if 'close' not in self.df.columns:
                raise KeyError("The DataFrame must contain a 'close' column for trade execution.")

            for i in range(len(self.df)):
                signal = self.signals.iloc[i]
                close_price = self.df['close'].iloc[i]

                if signal == 'buy' and not self.positions:
                    # Buy action
                    self.positions.append(close_price)
                    self.balance -= close_price * (1 + self.fee)
                    self.trade_history.append({'action': 'buy', 'price': close_price, 'balance': self.balance})

                elif signal == 'sell' and self.positions:
                    # Sell action
                    entry_price = self.positions.pop()
                    profit = close_price - entry_price
                    self.balance += close_price * (1 - self.fee)
                    self.trade_history.append({'action': 'sell', 'price': close_price, 'profit': profit, 'balance': self.balance})

            # Debugging output
            print("Final Balance:", self.balance)
            print("Trade History:")
            print(pd.DataFrame(self.trade_history))
        except Exception as e:
            print(f"Error during trade execution: {e}")

if __name__ == "__main__":
    # Example data
    df = pd.DataFrame({
        'close': [100, 102, 101, 103, 105],
        'signal': ['hold', 'buy', 'hold', 'sell', 'hold']
    }, index=pd.date_range(start='2023-01-01', periods=5, freq='D'))

    signals = df['signal']

    backtester = Backtester(df, signals)
    backtester.execute_trades()

    # Debugging output for processed data
    print("Processed Data:")
    print(df.head())