import numpy as np
import datetime as dt

from beartype.typing import List
from tqdm import tqdm

from stockMarket.utils import Period
from .technicals import Technicals


class Strategy:
    def __init__(self, tickers: List[str] | str):
        self.tickers = np.atleast_1d(tickers)

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
        n_bars = np.ceil(period_time / self.candle_period.period_time.days)
        n_bars = int(n_bars) + 10

        start_index = np.ceil((today - end).days /
                              self.candle_period.period_time.days).astype(int)
        end_index = np.ceil((today - start).days /
                            self.candle_period.period_time.days).astype(int)

        start_index = start_index + 1
        end_index = end_index + 1

        print(start_index, end_index, n_bars)

        for ticker in tqdm(self.tickers):
            contract = Technicals(ticker=ticker)
            contract.init_pricing_data(
                self.candle_period, n_bars=n_bars)

            for index in range(start_index, end_index + 1):
                pass
