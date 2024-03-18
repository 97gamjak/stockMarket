"""
Important Abbreviations for price levels:
- TP: Take Profit
- TP_B: Take Profit Body
- SL: Stop Loss
- SL_B: Stop Loss Body
- TC: Trigger Candle (Candle that triggers the trade)
- TC_B: Trigger Candle Body
- LOW: Lowest Low between ENTRY and TP
- LOW_B: Lowest Low Body between ENTRY and TP
- ENTRY: Entry
- R_ENTRY: Real Entry
- EXIT: Exit

General Abbreviations:
- CDist: Candle Distance
- PDist: Price Distance
- PL: Profit Loss
"""

import datetime as dt
import pandas as pd
import yfinance as yf
import numpy as np

from beartype.typing import Optional
from scipy import stats

from stockMarket.yfinance._common import adjust_price_data_from_df
from .enums import ChartEnum, TradeStatus
from .tradeSettings import TradeSettings
from .decorators import ignore_trade_exceptions, check_trade_status
from .common import calc_highest_body_price, calc_lowest_body_price


class Trade:
    def __init__(self,
                 ticker: str,
                 trigger_candle: pd.DataFrame,
                 settings=None,
                 ) -> None:

        self.ticker = ticker
        self.TC = trigger_candle

        self.ENTRY_date: Optional[dt.date] = None
        self.EXIT_date: Optional[dt.date] = None
        self.TP_date: Optional[dt.date] = None

        self.R_ENTRY: Optional[float] = None
        self.EXIT: Optional[float] = None
        self.TP: Optional[float] = None

        self.condition = None

        self.trade_executed = True
        self.trade_status = TradeStatus.UNKNOWN
        self.settings = settings if settings is not None else TradeSettings()

    @ignore_trade_exceptions
    def execute_trade(self, pricing: pd.DataFrame):
        self.TC_index = pricing.index.get_loc(self.TC.name)

        self.setup_TP(
            pricing,
            self.settings.max_CandleDist_TP_ENTRY
        )

        self.calculate_LOW_between_ENTRY_and_TP(
            pricing=pricing,
            ENTRY_index=self.TC_index,
            TP_index=self.TP_index
        )

        self.check_TP_TC_to_LOW_RATIO()

        self.check_PL_RATIOS()

        self.calc_R_ENTRY(pricing)

        # if low_index == self.candle_index:
        #     self.trade_executed = False
        #     return

        # start_index = self.candle_index - 25 if self.candle_index - 25 > 0 else 0

        # slope, intercept, r, p, std_err = stats.linregress(
        #     np.arange(start_index, self.candle_index + 1), pricing.close[start_index:self.candle_index+1])

        # if slope < 0:
        #     self.trade_executed = False
        #     return

        EXIT_index, EXIT_reason = self.find_exit(pricing)

        self.calc_EXIT(pricing, EXIT_index,
                       EXIT_reason, self.ENTRY_date)

    @check_trade_status
    def check_PL_RATIOS(self):

        self.PL = (self.TP - self.ENTRY) / (self.ENTRY - self.SL)

        if self.settings.min_PL is not None and self.PL < self.settings.min_PL:
            self.trade_executed = False
            self.trade_status = TradeStatus.PL_TOO_SMALL

        if self.settings.max_PL is not None and self.PL > self.settings.max_PL:
            self.trade_executed = False
            self.trade_status = TradeStatus.PL_TOO_LARGE

    def find_exit(self, pricing: pd.DataFrame):
        for i in range(self.TC_index+1, len(pricing)):
            candle = pricing.iloc[i]
            if candle.low <= self.SL and candle.high >= self.TP:
                return i, "ambiguous"

            if candle.low <= self.SL:
                return i, "stop_loss"

            if candle.high >= self.TP:
                return i, "target"

        return None, None

    @check_trade_status
    def setup_TP(self, pricing: pd.DataFrame, max_candles: int = 10):
        if self.settings.TP_strategy == ChartEnum.LAST_HIGH:
            TP, TP_index = self.find_last_high(
                pricing, max_candles)
        else:
            raise NotImplementedError(
                f"Invalid take profit setting {self.settings.TP_strategy}")

        if TP is None:
            self.trade_executed = False
            self.trade_status = TradeStatus.TP_NOT_FOUND
            return

        TP_date = self.calc_take_profit_date(
            pricing, TP_index, TP)

        self.TP = TP
        self.TP_date = TP_date
        self.TP_index = TP_index
        self.max_TP_B = calc_highest_body_price(
            pricing.iloc[self.TP_index])

    def find_last_high(self, pricing: pd.DataFrame, max_candles: int = 10):
        high = self.TC.high
        highest_body_price = max(
            self.TC.open, self.TC.close)
        high_index = self.TC_index

        for i in range(1, max_candles):
            candle = pricing.iloc[self.TC_index - i]
            _highest_body_price = calc_highest_body_price(candle)
            if (high_index == self.TC_index and candle.high > high * 1.03):
                if _highest_body_price < highest_body_price*1.03:
                    continue
                high = candle.high
                high_index = self.TC_index - i
                highest_body_price = _highest_body_price
            if (high_index != self.TC_index and candle.high > high):
                high = candle.high
                high_index = self.TC_index - i
                highest_body_price = _highest_body_price
            elif high_index != self.TC_index and (_highest_body_price - self.SL) / (highest_body_price - self.SL) < 0.95:
                break

        if self.TC_index == high_index:
            return None, None
        else:
            return high, high_index

    def calc_take_profit_date(self, pricing: pd.DataFrame, target_candle_index, take_profit):
        return self.calc_daily_candle(pricing, target_candle_index, take_profit)[1]

    @check_trade_status
    def calculate_LOW_between_ENTRY_and_TP(self, pricing, ENTRY_index, TP_index):

        self.low, self.LOW_index = self.find_last_low(
            pricing, ENTRY_index - TP_index)

        if self.settings.max_SL_LOW_to_ENTRY_RATIO is not None:
            if (self.ENTRY - self.low) / (self.ENTRY - self.SL) > self.settings.max_SL_LOW_to_ENTRY_RATIO:
                self.trade_executed = False
                self.trade_status = TradeStatus.LOW_SL_RATIO_TOO_LARGE
                return

        self.min_LOW_B = calc_lowest_body_price(
            pricing.iloc[self.LOW_index])

    def find_last_low(self, pricing: pd.DataFrame, max_candles: int = 6):

        LOW = self.SL
        LOW_index = self.TC_index

        for i in range(0, max_candles+1):
            candle = pricing.iloc[self.TC_index - i]
            if candle.low < LOW:
                LOW = candle.low
                LOW_index = self.TC_index - i

        return LOW, LOW_index

    @check_trade_status
    def check_TP_TC_to_LOW_RATIO(self):
        if self.settings.min_TP_B_TC_B_to_LOW_RATIO is not None:
            if (self.max_TP_B - self.low) / (self.max_TC_B - self.low) < self.settings.min_TP_B_TC_B_to_LOW_RATIO:
                self.trade_executed = False
                self.trade_status = TradeStatus.TP_B_TC_B_TO_LOW_RATIO_TOO_SMALL

    def calc_R_ENTRY(self, pricing: pd.DataFrame):

        if self.TC_index != len(pricing)-1:
            self.R_ENTRY, self.ENTRY_date = self.calc_daily_candle(
                pricing,
                self.TC_index+1,
                self.ENTRY,
                limit=self.settings.loss_limit
            )
            if self.R_ENTRY is None:
                self.trade_executed = False
                self.trade_status = TradeStatus.NO_ENTRY_WITHIN_NEXT_INTERVAL

        if self.R_ENTRY is None:
            self.trade_executed = False
            self.trade_status = TradeStatus.TO_BE_DETERMINED

    def calc_EXIT(self, pricing: pd.DataFrame, EXIT_index, EXIT_reason, ENTRY_date):
        if EXIT_reason == "target":

            self.EXIT = self.TP
            _, self.EXIT_date = self.calc_daily_candle(
                pricing,
                EXIT_index,
                self.TP,
                min_date=ENTRY_date
            )

        elif EXIT_reason == "stop_loss":

            self.EXIT, self.EXIT_date = self.calc_daily_candle(
                pricing,
                EXIT_index,
                self.SL,
                np.less_equal,
                min_date=ENTRY_date
            )

        elif EXIT_reason == "ambiguous":

            TP, TP_date = self.calc_daily_candle(
                pricing,
                EXIT_index,
                self.TP,
                min_date=ENTRY_date
            )
            _, SL_date = self.calc_daily_candle(
                pricing,
                EXIT_index,
                self.SL,
                np.less_equal,
                min_date=ENTRY_date
            )

            if TP_date is None and SL_date is None:
                # TODO: think of a way to check next interval in this case
                raise ValueError("No exit date found")
            elif TP_date is None:
                TP_date = SL_date + pd.Timedelta(days=1)
            elif SL_date is None:
                SL_date = TP_date + pd.Timedelta(days=1)

            if TP_date > SL_date:
                self.EXIT = self.SL
                self.EXIT_date = SL_date
            elif TP_date < SL_date:
                self.EXIT = self.TP
                self.EXIT_date = TP_date
            else:
                ticker = yf.Ticker(self.ticker)
                prices = ticker.history(
                    auto_adjust=False,
                    start=str(TP_date),
                    end=None,
                    rounding=True
                )
                prices = adjust_price_data_from_df(prices).iloc[0]

                if prices.open <= self.SL:
                    self.EXIT = self.SL
                elif prices.open >= self.TP:
                    self.EXIT = TP
                else:
                    self.EXIT = None
                    self.trade_status = 

                self.EXIT_date = TP_date

    def calc_daily_candle(self,
                          pricing: pd.DataFrame,
                          candle_index: int,
                          target_price: float,
                          mode=np.greater_equal,
                          limit=None,
                          min_date=None,
                          ):
        start_date = pricing.index[candle_index].date()
        if candle_index == len(pricing)-1:
            end_date = None
        else:
            # end date can be set to the next candle date for all intervals
            # e.g if intervall is weekly than end date is the next week but
            # yf will not include the first day of the next week
            end_date = pricing.index[candle_index + 1].date()
            end_date = str(end_date)

        ticker = yf.Ticker(self.ticker)
        pricing_daily = ticker.history(
            auto_adjust=False,
            start=str(start_date),
            end=end_date,
            rounding=True
        )
        pricing_daily = adjust_price_data_from_df(pricing_daily)

        price = None
        date = None

        for i in range(len(pricing_daily)):
            if min_date is not None and pricing_daily.index[i].date() < min_date:
                continue
            price_open = pricing_daily.iloc[i].open
            price_low = pricing_daily.iloc[i].low
            price_high = pricing_daily.iloc[i].high
            if mode == np.greater_equal:
                check_price = price_high
            else:
                check_price = price_low
            date = pricing_daily.index[i].date()
            if mode(price_open, target_price):
                price = price_open

                # only fast hack to make a stop limit entry order
                if limit is not None:
                    if mode((price_open - self.SL)/(target_price - self.SL), limit):
                        if not mode((price_low - self.SL)/(target_price - self.SL), limit):
                            price = limit * \
                                (target_price - self.SL) + \
                                self.SL
                            break
                    else:
                        break
                else:
                    break

            elif mode(check_price, target_price):
                price = target_price
                break

            price, date = None, None

        return price, date

    @property
    def TC_date(self):
        return self.TC.name.date()

    @property
    def ENTRY(self):
        return self.TC.close

    @property
    def SL(self):
        return self.TC.low

    @property
    def max_TC_B(self):
        return calc_highest_body_price(self.TC)

    @property
    def min_TC_B(self):
        return calc_lowest_body_price(self.TC)
