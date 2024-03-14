import os
import numpy as np
import datetime as dt

from beartype.typing import List
from tqdm import tqdm

from stockMarket.utils import Period, Caching


class StrategyBase:
    def __init__(self, tickers: List[str] | str):
        Caching.clear_cache()
        self.tickers = sorted(np.atleast_1d(tickers))

    def screen(self,
               candle_period: str | Period | None = None,
               start=None,
               end=None,
               ) -> None:

        if candle_period is None:
            self.candle_period = Period('daily')
        else:
            self.candle_period = Period(candle_period)

        today = dt.datetime.now().date()
        if start is None:
            start = today
        else:
            start = dt.datetime.strptime(start, "%d.%m.%Y").date()
        if end is None:
            end = today
        else:
            end = dt.datetime.strptime(end, "%d.%m.%Y").date()

        if end < start:
            raise ValueError("End date must be greater than start date")

        period_time = (today - start).days + 1
        self.n_bars = np.ceil(
            period_time / self.candle_period.period_time.days)
        self.n_bars = int(self.n_bars) + 100

        self.start_index = np.ceil((today - end).days /
                                   self.candle_period.period_time.days).astype(int)
        self.end_index = np.ceil((today - start).days /
                                 self.candle_period.period_time.days).astype(int)

        self.start_index = self.start_index + 1
        self.end_index = self.end_index + 1
