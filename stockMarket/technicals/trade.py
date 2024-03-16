import datetime as dt
import pandas as pd
import yfinance as yf

from beartype.typing import Optional

from stockMarket.utils import Period
from stockMarket.technicals.technicals import Technicals


class Trade:
    def __init__(self, ticker: str, trigger_candle: pd.DataFrame) -> None:
        self.ticker = ticker
        self.trigger_candle = trigger_candle

        self.entry_date: Optional[dt.date] = None
        self._target_date: Optional[dt.date]
        self._close_date: Optional[dt.date]
        self._exit_date: Optional[dt.date] = None

        self.real_entry_price: Optional[float] = None
        self._take_profit: Optional[float]
        self._exit_price: Optional[float] = None

        self.trade_executed = True

    def execute_trade(self, pricing: pd.DataFrame):
        self.candle_index = pricing.index.get_loc(self.trigger_candle.name)
        low, low_index = self.find_low(pricing)
        if low is None:
            self.trade_executed = False
            return

    def find_next_low(self, pricing: pd.DataFrame, max_candles: int = 6):

        low = self.stop_loss
        low_index = self.candle_index

        max_candles_to_check = min(100, len(pricing) - self.candle_index)

        i = 1

        while i < max_candles_to_check:
            candle = pricing.iloc[self.candle_index - i]
            if candle.low < low:
                low = candle.low
                low_index = self.candle_index - i
                break

        if low_index == self.candle_index:
            return None, None
        else:
            return low, low_index

    def candle_body_center(self, candle: pd.DataFrame):
        return (candle.open + candle.close) / 2

    def calc_real_entry(self, pricing: pd.DataFrame):
        candle_index = pricing.index.get_loc(self.trigger_candle.name)
        next_candle_date = pricing.index[candle_index + 1].date()
        last_daily_candle = next_candle_date - pd.Timedelta(days=1)

        ticker = yf.Ticker(self.ticker)
        pricing_daily = ticker.history(
            start=str(next_candle_date), end=str(last_daily_candle), rounding=True)

        self.real_entry_price = None

        for i in range(len(pricing)):
            price_open = pricing_daily.iloc[i].Open
            price_high = pricing_daily.iloc[i].High
            self.entry_date = pricing_daily.index[i].date()
            if price_open >= self.entry_price:
                self.real_entry_price = price_open
                break
            elif price_high >= self.entry_price:
                self.real_entry_price = self.entry_price
                break

            self.real_entry_price = None
            self.entry_date = None

        if self.real_entry_price is None or self.entry_date is None:
            self.trade_executed = False

    def calc_target(self, pricing: pd.DataFrame):
        candle_index = pricing.index.get_loc(self.trigger_candle.name)
        max_candle_date = pricing.index[candle_index - 20].date()
        last_daily_candle = max_candle_date - pd.Timedelta(days=1)

        ticker = yf.Ticker(self.ticker)
        pricing_daily = ticker.history(
            start=str(max_candle_date), end=str(last_daily_candle), rounding=True)

    @property
    def candle_date(self):
        return self.trigger_candle.name.date()

    @property
    def entry_price(self):
        return self.trigger_candle.close

    @property
    def stop_loss(self):
        return self.trigger_candle.low
