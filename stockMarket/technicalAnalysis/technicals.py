import pandas as pd
import numpy as np
import mplfinance as mpf
import talib
import warnings

from tvDatafeed import TvDatafeed

from stockMarket.core.contract import Contract
from stockMarket.utils import Period
from .indicators import EMA


class Technicals:
    def __init__(self, contract: Contract | None = None, ticker: str | None = None, exchange: str | None = ""):
        if contract:
            if ticker or exchange == "":
                warnings.warn(
                    "ticker and exchange are ignored when contract is provided")

            self.contract = contract
            self.ticker = contract.ticker
            self.exchange = contract.exchange
        else:
            self.contract = Contract(ticker=ticker, exchange=exchange)
            self.ticker = ticker
            self.exchange = exchange

        self.pricing_data = None

    def init_pricing_data(self, interval: Period = "daily", n_bars: int | None = 1000):
        if n_bars is None:
            n_bars = 5000  # max value

        interval = Period(interval)

        tv = TvDatafeed()
        self.pricing_data = tv.get_hist(
            symbol=self.ticker,
            exchange=self.exchange,
            interval=interval.interval,
            n_bars=n_bars,
        )

    def rsi(self, time_period: int = 14):
        self.rsi = talib.RSI(self.pricing_data.close, timeperiod=time_period)
        return self.rsi

    def macd(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        self.macd = talib.MACD(self.pricing_data.close, fastperiod=fast_period,
                               slowperiod=slow_period, signalperiod=signal_period)
        return self.macd

    def bbands(self, nbdevup: int = 2, nbdevdn: int = 2, time_period: int = 20):
        self.bbands = talib.BBANDS(
            self.pricing_data.close, nbdevup=nbdevup, nbdevdn=nbdevdn, timeperiod=time_period)
        return self.bbands

    def calc_ema(self, length: int = 20):
        self.ema = EMA(self.pricing_data.close, length).calculate()
        return self.ema

    def plot(self, logarithmic_scale="linear", **kwargs):
        add_plots = []

        for i, (key, value) in enumerate(kwargs.items()):
            add_plots += plot_map[key](value, i+2)

        bucket_size = 0.001 * max(self.pricing_data["close"])
        vol_profile = self.pricing_data["volume"].groupby(self.pricing_data["close"].apply(
            lambda x: bucket_size * round(x/bucket_size, 0))).sum()

        mc = mpf.make_marketcolors(base_mpf_style="yahoo")
        s = mpf.make_mpf_style(base_mpf_style="yahoo", marketcolors=mc)

        fig, axlist = mpf.plot(self.pricing_data, type="candle", addplot=add_plots, returnfig=True,
                               warn_too_much_data=10000, volume=True, style=s, figscale=1.3, yscale=logarithmic_scale)
        axlist[0].set_title(self.ticker, fontsize=20)
        vpax = fig.add_axes(axlist[0].get_position())
        vpax.set_axis_off()
        vpax.set_xlim(right=1.2*max(vol_profile.values))
        vpax.barh(vol_profile.keys().values, vol_profile.values,
                  height=0.75*bucket_size, align="center", color="black", alpha=0.45)


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


def _plot_bbands(bbands, _):
    panel = 0
    add_plots = []

    add_plots += [mpf.make_addplot(bbands[0], panel=panel,
                                   color='orange', secondary_y=False)]
    add_plots += [mpf.make_addplot(bbands[1],
                                   panel=panel, color='blue', secondary_y=False)]
    add_plots += [mpf.make_addplot(bbands[2], panel=panel,
                                   color='orange', secondary_y=False)]

    return add_plots


plot_map = {
    "rsi": _plot_rsi,
    "macd": _plot_macd,
    "bbands": _plot_bbands,
}
