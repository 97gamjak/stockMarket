import datetime as dt
import pandas as pd
import warnings

from tvDatafeed import TvDatafeed

from stockMarket.utils import Period
from stockMarket import __data_path__


class Pricing:
    def __init__(self, ticker: str, exchange: str = ""):
        self.ticker = ticker
        self.exchange = exchange

    def get_pricing_data(self):
        file = __data_path__ / f"prices/{self.ticker}_daily_prices.csv"
        if file.exists():
            self.prices = pd.read_csv(
                file, parse_dates=True, sep='\t', index_col=0)
            dates = [pd.to_datetime(date).date()
                     for date in self.prices.index.to_series()]
            self.prices.index = dates
        else:
            warnings.warn(f"No prices available for {self.ticker}")
            self.prices = None

        return self.prices

    def update_prices(self, interval="daily", n_bars=5000):
        interval = Period(interval)

        tv = TvDatafeed()

        self.prices = tv.get_hist(
            symbol=self.ticker,
            exchange=self.exchange,
            interval=interval.interval,
            n_bars=n_bars,
        )

        filename = __data_path__ / \
            f"prices/{self.ticker}_{interval.period_string}_prices.csv"

        known_prices = self.load_known_prices(filename)
        if known_prices is None and self.prices is None:
            warnings.warn(f"No prices available for {self.ticker}")
            return

        all_prices = pd.concat(
            [known_prices, self.prices], axis=0)
        all_prices = all_prices[~all_prices.index.duplicated(keep='last')]
        all_prices = all_prices.sort_index()
        all_prices.to_csv(filename, sep='\t',
                          encoding='utf-8', float_format='%.2f', index=True)

    def load_known_prices(self, filename):
        if filename.exists():
            return pd.read_csv(filename, parse_dates=True, index_col=0, sep='\t')
        else:
            return None
