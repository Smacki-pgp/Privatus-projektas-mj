import pandas as pd
import ccxt

class DataFetcher:
    def __init__(self, symbol, timeframe):
        self.symbol = symbol
        self.timeframe = timeframe
        self.exchange = ccxt.binance()

    def fetch_data(self):
        ohlcv = self.exchange.fetch_ohlcv(self.symbol, self.timeframe)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        return df