import pandas as pd
import numpy as np

class MetricsCalculator:
    def __init__(self, df, initial_balance):
        """
        Initializes the MetricsCalculator with trading data.

        :param df: DataFrame containing trade and equity information.
        :param initial_balance: Initial balance for the portfolio.
        """
        self.df = df
        self.initial_balance = initial_balance
        self.metrics = {}

    def calculate_metrics(self):
        """
        Calculates key performance metrics for the trading strategy.

        :return: Dictionary containing calculated metrics.
        """
        try:
            if self.df.empty:
                raise ValueError("DataFrame cannot be empty for metrics calculation.")

            if 'close' not in self.df.columns or 'equity' not in self.df.columns:
                raise KeyError("DataFrame must contain 'close' and 'equity' columns.")

            equity_curve = self.df['equity']
            duration = (self.df.index[-1] - self.df.index[0]).days

            # Exposure time percentage
            exposure_time = self.df['exposure'].mean() * 100 if 'exposure' in self.df.columns else 0

            # Equity metrics
            equity_final = equity_curve.iloc[-1]
            equity_peak = equity_curve.cummax().max()

            # Return calculations
            return_percent = (equity_final - self.initial_balance) / self.initial_balance * 100
            buy_and_hold_return = ((self.df['close'].iloc[-1] - self.df['close'].iloc[0]) / self.df['close'].iloc[0]) * 100
            return_annual_percent = (1 + return_percent / 100) ** (365 / duration) - 1 if duration > 0 else 0

            # Volatility and performance ratios
            daily_returns = equity_curve.pct_change().dropna()
            volatility_annual_percent = daily_returns.std() * np.sqrt(252) * 100
            sharpe_ratio = (daily_returns.mean() / daily_returns.std() * np.sqrt(252)) if daily_returns.std() > 0 else 0

            downside_returns = daily_returns[daily_returns < 0]
            sortino_ratio = (daily_returns.mean() / downside_returns.std() * np.sqrt(252)) if downside_returns.std() > 0 else 0

            max_drawdown = (equity_curve / equity_curve.cummax() - 1).min() * 100
            calmar_ratio = return_annual_percent / abs(max_drawdown) if max_drawdown != 0 else 0

            # Drawdown metrics
            avg_drawdown = self.df['drawdown'].mean() * 100 if 'drawdown' in self.df.columns else 0
            max_drawdown_duration = self._calculate_max_drawdown_duration(equity_curve)

            # Trade metrics
            trades = self.df[self.df['trade_signal'].notnull()] if 'trade_signal' in self.df.columns else pd.DataFrame()
            total_trades = len(trades)
            win_rate = len(trades[trades['pnl'] > 0]) / total_trades * 100 if total_trades > 0 else 0
            best_trade = trades['pnl'].max() * 100 if not trades.empty else 0
            worst_trade = trades['pnl'].min() * 100 if not trades.empty else 0
            avg_trade = trades['pnl'].mean() * 100 if not trades.empty else 0
            trade_durations = trades['duration'] if 'duration' in trades.columns else pd.Series(dtype=float)
            max_trade_duration = trade_durations.max() if not trade_durations.empty else 0
            avg_trade_duration = trade_durations.mean() if not trade_durations.empty else 0

            # Store metrics
            self.metrics = {
                'Duration (days)': duration,
                'Exposure Time (%)': exposure_time,
                'Equity Final': equity_final,
                'Equity Peak': equity_peak,
                'Return (%)': return_percent,
                'Buy and Hold Return (%)': buy_and_hold_return,
                'Return Annual (%)': return_annual_percent * 100,
                'Volatility Annual (%)': volatility_annual_percent,
                'Sharpe Ratio': sharpe_ratio,
                'Sortino Ratio': sortino_ratio,
                'Calmar Ratio': calmar_ratio,
                'Max Drawdown (%)': max_drawdown,
                'Avg Drawdown (%)': avg_drawdown,
                'Max Drawdown Duration (days)': max_drawdown_duration,
                'Total Trades': total_trades,
                'Win Rate (%)': win_rate,
                'Best Trade (%)': best_trade,
                'Worst Trade (%)': worst_trade,
                'Avg Trade (%)': avg_trade,
                'Max Trade Duration': max_trade_duration,
                'Avg Trade Duration': avg_trade_duration
            }

            # Debugging output
            print("Calculated Metrics:")
            for key, value in self.metrics.items():
                print(f"{key}: {value}")

            return self.metrics
        except Exception as e:
            print(f"Error calculating metrics: {e}")
            return {}

    def _calculate_max_drawdown_duration(self, equity_curve):
        """
        Calculates the maximum duration of a drawdown.

        :param equity_curve: Series representing the equity curve.
        :return: Maximum drawdown duration in days.
        """
        drawdown = equity_curve / equity_curve.cummax() - 1
        is_drawdown = drawdown < 0
        drawdown_durations = is_drawdown.astype(int).groupby((~is_drawdown).cumsum()).cumsum()
        return drawdown_durations.max() if not drawdown_durations.empty else 0

if __name__ == "__main__":
    # Example data
    df = pd.DataFrame({
        'close': [100, 102, 101, 103, 105],
        'equity': [10000, 10200, 10150, 10300, 10500],
        'exposure': [1, 1, 0, 1, 1],
        'drawdown': [0, -0.01, -0.02, 0, 0],
        'trade_signal': [None, 'buy', None, 'sell', None],
        'pnl': [0, 200, None, 150, None],
        'duration': [None, 2, None, 3, None]
    }, index=pd.date_range(start='2023-01-01', periods=5, freq='D'))

    calculator = MetricsCalculator(df, initial_balance=10000)
    metrics = calculator.calculate_metrics()

    print("Metrics:")
    for key, value in metrics.items():
        print(f"{key}: {value}")
