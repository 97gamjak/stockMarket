from __future__ import annotations

import pandas as pd
import matplotlib.pyplot as plt
import talib
import numpy as np

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

    @property
    def ebitda(self):
        depreciation = np.nan_to_num(self.cashflow.depreciation)
        amortization = np.nan_to_num(self.cashflow.amortization)
        return self.income.ebit + depreciation + amortization

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
        n_subplots = len(kwargs) + 1
        fig, ax = plt.subplots(n_subplots, 1, sharex=True)
        ax[0].set_title(self.ticker)
        ax[0] = _plot_pricing(ax[0], self._pricing_data["close"])

        for i, (key, value) in enumerate(kwargs.items()):
            ax[i+1] = plot_map[key](ax[i+1], value)

        fig.set_size_inches(18.5, 10.5)
        plt.show()


def _plot_pricing(ax: plt.Axes, pricing_data=None):
    ax.plot(pricing_data)
    ax.set_ylabel("Close")

    return ax


def _plot_rsi(ax: plt.Axes, rsi):
    ax.plot(rsi, c="orange")
    ax.axhline(y=70, c="red", linestyle="--")
    ax.axhline(y=30, c="green", linestyle="--")
    ax.set_ylabel("RSI")

    return ax


def _plot_macd(ax: plt.Axes, macd):
    colormat = np.where(macd[2] > 0, 'g', 'r')
    ax.plot(macd[0], c="blue", label="macd-fastperiod")
    ax.plot(macd[1], c="orange", label="macd-slowperiod")
    ax.bar(macd[2].index, macd[2].values,
           color=colormat, label="macd-histogram")
    ax.set_ylabel("MACD")
    ax.legend(loc="upper left")

    return ax


plot_map = {
    "rsi": _plot_rsi,
    "macd": _plot_macd
}
