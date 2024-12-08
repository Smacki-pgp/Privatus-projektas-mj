import pandas as pd

class DataProcessor:
    def __init__(self, df_asset, df_benchmark):
        self.df_asset = df_asset
        self.df_benchmark = df_benchmark

    def calculate_indicators(self):
        # Calculate RRS
        self.df_asset['RRS'] = self.df_asset['close'] / self.df_benchmark['close']
        return self.df_asset