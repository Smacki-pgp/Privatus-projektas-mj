import config
import pandas as pd

class Backtester:
    def __init__(self, df, signals):
        self.df = df
        self.signals = signals
        self.balance = config.INITIAL_BALANCE

    def run_backtest(self):
        # Initialize backtesting variables
        initial_balance = self.balance
        positions = []
        trades = []

        for i in range(len(self.df)):
            if self.signals['signal'].iloc[i] == 'buy':
                # Execute buy order
                if not positions:
                    position_size = self.balance / self.signals['close'].iloc[i]
                    positions.append(position_size)
                    trades.append({'timestamp': self.signals.index[i], 'action': 'buy', 'price': self.signals['close'].iloc[i]})
                    self.balance -= position_size * self.signals['close'].iloc[i]

            elif self.signals['signal'].iloc[i] == 'sell':
                # Execute sell order
                if positions:
                    for j in range(len(positions)):
                        position_value = positions[j] * self.signals['close'].iloc[i]
                        trades.append({'timestamp': self.signals.index[i], 'action': 'sell', 'price': self.signals['close'].iloc[i]})
                        self.balance += position_value
                        del positions[j]

        # Calculate performance metrics
        final_balance = self.balance
        total_trades = len(trades)
        profit_loss = final_balance - initial_balance

        # Print backtest results
        print(f"Initial Balance: {initial_balance}")
        print(f"Final Balance: {final_balance}")
        print(f"Profit/Loss: {profit_loss}")
        print(f"Total Trades: {total_trades}")

        return {
            'initial_balance': initial_balance,
            'final_balance': final_balance,
            'profit_loss': profit_loss,
            'total_trades': total_trades
        }