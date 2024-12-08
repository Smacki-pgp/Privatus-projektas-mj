import pandas as pd

class Strategy:
    def __init__(self, buy_threshold, sell_threshold):
        """
        Initializes the Strategy with buy and sell thresholds.

        :param buy_threshold: Threshold for generating buy signals.
        :param sell_threshold: Threshold for generating sell signals.
        """
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold

    def generate_signals(self, df):
        """
        Generates buy, sell, and hold signals based on the provided DataFrame.

        :param df: DataFrame containing the required data and indicators.
        :return: Series containing signals ('buy', 'sell', 'hold').
        """
        try:
            if df.empty:
                raise ValueError("Input DataFrame cannot be empty.")

            if 'RRS' not in df.columns:
                raise ValueError("DataFrame must contain 'RRS' column for signal generation.")

            # Initialize signals as 'hold'
            signals = pd.Series(index=df.index, data='hold', dtype='str')

            # Generate buy signals where RRS exceeds the buy threshold
            signals.loc[df['RRS'] > self.buy_threshold] = 'buy'

            # Generate sell signals where RRS falls below the sell threshold
            signals.loc[df['RRS'] < self.sell_threshold] = 'sell'

            # Add signal reasons to the DataFrame for debugging and analysis
            df['signal_reason'] = 'None'
            df.loc[df['RRS'] > self.buy_threshold, 'signal_reason'] = 'RRS above buy threshold'
            df.loc[df['RRS'] < self.sell_threshold, 'signal_reason'] = 'RRS below sell threshold'

            # Debugging output
            print("Generated Signals:")
            print(signals.head())
            print("\nSignal Reasons:")
            print(df[['RRS', 'signal_reason']].head())

            return signals
        except Exception as e:
            print(f"Error generating signals: {e}")
            return pd.Series(dtype='str')

    def calculate_signal_strength(self, df):
        """
        Calculates the strength of buy and sell signals based on the RRS distance from thresholds.

        :param df: DataFrame containing the 'RRS' column.
        :return: Series with signal strength values.
        """
        try:
            if df.empty:
                raise ValueError("Input DataFrame cannot be empty for signal strength calculation.")

            if 'RRS' not in df.columns:
                raise ValueError("DataFrame must contain 'RRS' column for signal strength calculation.")

            # Initialize signal strength as 0
            signal_strength = pd.Series(index=df.index, data=0.0, dtype=float)

            # Calculate positive signal strength for buy signals
            signal_strength.loc[df['RRS'] > self.buy_threshold] = df['RRS'] - self.buy_threshold

            # Calculate negative signal strength for sell signals
            signal_strength.loc[df['RRS'] < self.sell_threshold] = self.sell_threshold - df['RRS']

            # Debugging output
            print("Signal Strengths:")
            print(signal_strength.head())

            return signal_strength
        except Exception as e:
            print(f"Error calculating signal strength: {e}")
            return pd.Series(dtype=float)

if __name__ == "__main__":
    # Example data
    df = pd.DataFrame({
        'RRS': [1.0, 1.05, 1.02, 0.97, 1.01, 0.96, 1.03]
    }, index=pd.date_range(start='2023-01-01', periods=7, freq='D'))

    # Initialize Strategy with thresholds
    strategy = Strategy(buy_threshold=1.02, sell_threshold=0.98)

    # Generate signals
    signals = strategy.generate_signals(df)

    # Calculate signal strength
    signal_strength = strategy.calculate_signal_strength(df)

    print("Signals:")
    print(signals)
    print("\nSignal Strength:")
    print(signal_strength)
    print("\nDataFrame with Signal Reasons:")
    print(df)
