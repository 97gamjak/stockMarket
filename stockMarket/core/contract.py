from __future__ import annotations

import pandas as pd
import mplfinance as mpf
import talib
import numpy as np
import datetime as dt

from tvDatafeed import TvDatafeed, Interval
from dataclasses import dataclass, field

from .income import Income
from .financialStatement import BalanceSheet, CashFlow


@dataclass(kw_only=True)
class Contract:
    ticker: str
    exchange: str = ""
    income: Income = field(default_factory=Income)
    balance: BalanceSheet = field(default_factory=BalanceSheet)
    cashflow: CashFlow = field(default_factory=CashFlow)

    earnings_date: dt.datetime | None = None
    ex_dividend_date: dt.datetime | None = None

    @property
    def ebitda(self):
        depreciation = np.nan_to_num(self.cashflow.depreciation)
        amortization = np.nan_to_num(self.cashflow.amortization)
        return self.income.ebit + depreciation + amortization

    @property
    def ebitda_margin(self):
        return self.ebitda / self.income.revenue * 100

    def init_pricing_data(self, interval: Interval = Interval.in_daily, n_bars: int = 1000):
        tv = TvDatafeed()
        self._pricing_data = tv.get_hist(
            symbol=self.ticker,
            exchange=self.exchange,
            interval=interval,
            n_bars=n_bars,
        )

    def rsi(self, time_period: int = 14):
        return talib.RSI(self._pricing_data.close, timeperiod=time_period)

    def macd(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        return talib.MACD(self._pricing_data.close, fastperiod=fast_period, slowperiod=slow_period, signalperiod=signal_period)

    def plot(self, **kwargs):
        add_plots = []

        for i, (key, value) in enumerate(kwargs.items()):
            add_plots += plot_map[key](value, i+2)

        mpf.plot(self._pricing_data, addplot=add_plots,
                 warn_too_much_data=10000, volume=True, style="starsandstripes", figscale=1.3)


def _plot_rsi(rsi, panel: int):
    add_plots = []
    line30 = pd.Series(30, index=rsi.index)
    line70 = pd.Series(70, index=rsi.index)
    #fmt: off
    add_plots += [mpf.make_addplot(rsi, panel=panel, ylabel="RSI")]
    add_plots += [mpf.make_addplot(line30, panel=panel, secondary_y=False, color='g')]
    add_plots += [mpf.make_addplot(line70, panel=panel, secondary_y=False, color='r')]
    #fmt: on
    return add_plots


def _plot_macd(macd, panel: int):
    add_plots = []

    colormat = np.where(macd[2] > 0, 'g', 'r')

    add_plots += [mpf.make_addplot(macd[0], panel=panel,
                                   ylabel="MACD")]
    add_plots += [mpf.make_addplot(macd[1], panel=panel,
                                   color='orange', secondary_y=False)]
    add_plots += [mpf.make_addplot(macd[2], type='bar',
                                   panel=panel, color=colormat, secondary_y=False)]

    return add_plots


plot_map = {
    "rsi": _plot_rsi,
    "macd": _plot_macd
}
