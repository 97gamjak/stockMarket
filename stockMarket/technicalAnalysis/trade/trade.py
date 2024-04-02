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
import numpy as np

from beartype.typing import Optional

from .enums import ChartEnum, TradeStatus, TradeOutcome, AttachedOrderType
from .enums_api import determine_outcome_status, check_PL_ratio

from .tradeSettings import TradeSettings
from .decorators import ignore_trade_exceptions, check_trade_status
from ._mixins import PropertyMixin, JSONMixin
from .common import (
    calc_highest_body_price,
    calc_lowest_body_price,
    find_last_high,
)


class Trade(PropertyMixin, JSONMixin):
    def __init__(self,
                 ticker: str,
                 trigger_candle: pd.DataFrame,
                 settings: Optional[TradeSettings] = None,
                 ) -> None:

        self.ticker = ticker
        self.TC = trigger_candle

        self.ENTRY_date: Optional[dt.date] = None
        self.EXIT_date: Optional[dt.date] = None
        self.TP_date: Optional[dt.date] = None

        self.R_ENTRY: Optional[float] = None
        self.EXIT: Optional[float] = None
        self.TP: Optional[float] = None

        self.trade_status = TradeStatus.UNKNOWN
        self.settings = settings if settings is not None else TradeSettings()

        self.outcome_status = TradeOutcome.NONE

    @ignore_trade_exceptions
    def execute_trade(self,
                      pricing: pd.DataFrame,
                      pricing_daily: pd.DataFrame,
                      ) -> None:

        self.TC_index = pricing.index.get_loc(self.TC.name)

        self.setup_TP(
            pricing=pricing,
            pricing_daily=pricing_daily
        )

        self.calculate_LOW_between_ENTRY_and_TP(
            pricing=pricing,
        )

        self.check_TP_TC_to_LOW_RATIO()

        self.check_PL_RATIOS()

        self.calc_R_ENTRY(
            pricing=pricing,
            pricing_daily=pricing_daily
        )

        self.check_min_volatility()

        self.calc_EXIT(pricing_daily=pricing_daily)

        self.outcome_status = determine_outcome_status(
            self.trade_status,
            self.R_ENTRY,
            self.EXIT
        )

    @check_trade_status
    def check_PL_RATIOS(self):
        self.trade_status = check_PL_ratio(
            PL=self.PL,
            min_PL=self.settings.min_PL,
            max_PL=self.settings.max_PL
        )

    @check_trade_status
    def setup_TP(self,
                 pricing: pd.DataFrame,
                 pricing_daily: pd.DataFrame
                 ) -> None:

        if self.settings.TP_strategy == ChartEnum.LAST_HIGH:
            TP, TP_index = find_last_high(
                pricing=pricing,
                ref_candle_index=self.TC_index,
                max_candles=self.settings.max_CandleDist_TP_ENTRY,
                min_ratio_high_to_ref_candle=self.settings.min_ratio_high_to_ref_candle,
                max_drawdown_ratio_after_new_high=self.settings.max_drawdown_ratio_after_new_high,
            )
        else:
            raise NotImplementedError(
                f"Invalid take profit setting {self.settings.TP_strategy}")

        if TP is None:
            self.trade_status = TradeStatus.TP_NOT_FOUND
            return
        elif TP / self.TC.high < self.settings.min_ratio_high_to_ref_candle:
            self.trade_status = TradeStatus.TP_TC_HIGH_RATIO_TOO_SMALL
            return
        elif self.TC_index - TP_index - 1 < self.settings.min_candles_between_TP_and_ENTRY:
            self.trade_status = TradeStatus.NUMBER_OF_CANDLES_BETWEEN_TP_AND_TC_TOO_SMALL
            return

        TP_date = self.calc_TP_date(
            pricing_daily,
            pricing.iloc[TP_index],
            pricing.iloc[TP_index+1],
            TP
        )

        self.TP = TP
        self.TP_date = TP_date
        self.TP_index = TP_index
        self.max_TP_B = calc_highest_body_price(
            pricing.iloc[self.TP_index])

    def calc_TP_date(self,
                     pricing_daily: pd.DataFrame,
                     start_candle,
                     end_candle,
                     take_profit
                     ):

        start_date = start_candle.name
        end_date = end_candle.name

        dates_to_check = pricing_daily.index[pricing_daily.index >= start_date]
        dates_to_check = dates_to_check[dates_to_check < end_date]

        for date in dates_to_check:
            candle = pricing_daily.loc[date]
            if candle.high >= take_profit:
                return candle.name.date()

        return candle.name.date()

    @check_trade_status
    def calculate_LOW_between_ENTRY_and_TP(self, pricing: pd.DataFrame) -> None:

        self.low, self.LOW_index = self.find_last_low(
            pricing, self.TC_index - self.TP_index)

        if self.settings.max_LOW_SL_to_ENTRY_RATIO is not None:
            if (self.ENTRY - self.low) / (self.ENTRY - self.SL) > self.settings.max_LOW_SL_to_ENTRY_RATIO:
                self.trade_status = TradeStatus.LOW_SL_RATIO_TOO_LARGE
                return

        self.min_LOW_B = calc_lowest_body_price(
            pricing.iloc[self.LOW_index])

    # TODO: add here this max_candles as a settings parameter
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
                self.trade_status = TradeStatus.TP_B_TC_B_TO_LOW_RATIO_TOO_SMALL

    @check_trade_status
    def calc_R_ENTRY(self,
                     pricing: pd.DataFrame,
                     pricing_daily: pd.DataFrame
                     ) -> None:

        self.R_ENTRY = None
        self.ENTRY_date = None

        if self.TC_index + 1 == len(pricing):
            self.trade_status = TradeStatus.TO_BE_DETERMINED
            return

        date_to_start = pricing.index[self.TC_index+1]
        dates_to_check = pricing_daily.index[pricing_daily.index >= date_to_start]

        if self.TC_index + 2 < len(pricing):
            max_date = pricing.index[self.TC_index+2]
            dates_to_check = dates_to_check[dates_to_check < max_date]

        for date in dates_to_check:
            candle = pricing_daily.loc[date]

            if candle.high >= self.ENTRY:
                self.ENTRY_date = candle.name.date()
                R_ENTRY_candle = candle

                if candle.open >= self.ENTRY:
                    self.R_ENTRY = candle.open
                else:
                    self.R_ENTRY = self.ENTRY

                limit_ratio = (self.R_ENTRY - self.SL) / (self.ENTRY - self.SL)
                low_limit_ratio = (R_ENTRY_candle.low -
                                   self.SL)/(self.ENTRY - self.SL)

                # check if the loss limit is exceeded - if then the low limit is not exceeded
                # entry is set to the loss limit else search continues
                if self.settings.loss_limit is not None and limit_ratio > self.settings.loss_limit:
                    if low_limit_ratio < self.settings.loss_limit:
                        self.R_ENTRY = self.settings.loss_limit * \
                            (self.ENTRY - self.SL) + self.SL
                    else:
                        continue

                return

        # if no entry is found two possibilities exist:
        # 1. the entry is not found within the next interval
        # 2. the entry is to be determined if the next interval is not available
        if self.TC_index + 2 < len(pricing):
            self.trade_status = TradeStatus.NO_ENTRY_WITHIN_NEXT_INTERVAL
        else:
            self.trade_status = TradeStatus.TO_BE_DETERMINED

    @check_trade_status
    def check_min_volatility(self):
        if self.VOLATILITY < self.settings.min_volatility:
            self.trade_status = TradeStatus.VOLATILITY_TOO_SMALL

    def calc_EXIT(self,
                  pricing_daily: pd.DataFrame = None
                  ) -> None:

        if self.settings.attached_order_type == AttachedOrderType.STOP_LIMIT:
            self.EXIT_STOP_LIMIT(pricing_daily)
        elif self.settings.attached_order_type == AttachedOrderType.TRAILING_STOP_IF_TP_TOUCHED:
            self.EXIT_TRAILING_STOP_IF_TP_TOUCHED(pricing_daily)
        else:
            raise NotImplementedError(
                f"Invalid attached order type {self.settings.attached_order_type}")

    def EXIT_STOP_LIMIT(self, pricing_daily: pd.DataFrame):

        SL_EXIT, TP_EXIT, EXIT_candle, trade_status = self._EXIT_STOP_LIMIT(
            pricing_daily
        )

        if trade_status == TradeStatus.CLOSED:
            if TP_EXIT is None:
                self.EXIT = SL_EXIT
            else:
                self.EXIT = self.TP
            self.trade_status = trade_status
            self.EXIT_date = EXIT_candle.name.date()
        elif trade_status == TradeStatus.AMBIGUOUS_EXIT_DATE:
            self.trade_status = trade_status
            self.EXIT_date = EXIT_candle.name.date()

        elif EXIT_candle is None:
            self.trade_status = TradeStatus.OPEN

    def _EXIT_STOP_LIMIT(self, pricing_daily: pd.DataFrame):
        SL_EXIT = None
        TP_EXIT = None
        candle = None
        trade_status = TradeStatus.OPEN

        for date in pricing_daily.index[pricing_daily.index.date >= self.ENTRY_date]:
            candle = pricing_daily.loc[date]

            if candle.low <= self.SL:
                SL_EXIT = self.SL

            if candle.high >= self.TP:
                TP_EXIT = self.TP

            if SL_EXIT is not None and TP_EXIT is not None:
                if candle.open >= self.TP:
                    TP_EXIT = self.TP
                    SL_EXIT = None
                    trade_status = TradeStatus.CLOSED
                elif candle.open <= self.SL:
                    TP_EXIT = None
                    SL_EXIT = candle.open
                    trade_status = TradeStatus.CLOSED
                else:
                    trade_status = TradeStatus.AMBIGUOUS_EXIT_DATE

                break
            elif SL_EXIT is not None:
                if candle.open <= SL_EXIT:
                    SL_EXIT = candle.open
                trade_status = TradeStatus.CLOSED
                break
            elif TP_EXIT is not None:
                trade_status = TradeStatus.CLOSED
                break

            candle = None

        return SL_EXIT, TP_EXIT, candle, trade_status

    def EXIT_TRAILING_STOP_IF_TP_TOUCHED(self, pricing_daily: pd.DataFrame):

        SL_EXIT, TP_EXIT, EXIT_candle, trade_status = self._EXIT_STOP_LIMIT(
            pricing_daily
        )

        if trade_status == TradeStatus.CLOSED and TP_EXIT is None:
            self.EXIT = SL_EXIT
            self.trade_status = trade_status
            self.EXIT_date = EXIT_candle.name.date()
            return
        elif trade_status == TradeStatus.AMBIGUOUS_EXIT_DATE:
            self.trade_status = trade_status
            self.EXIT_date = EXIT_candle.name.date()
            return

        elif EXIT_candle is None:
            self.trade_status = TradeStatus.OPEN
            return

        high = self.TP
        trailing_stop_loss = high * (1 - self.settings.trailing_stop)
        new_stop_loss = False

        TP_candle = EXIT_candle
        for date in pricing_daily.index[pricing_daily.index >= TP_candle.name]:
            candle = pricing_daily.loc[date]
            EXIT_candle = None

            if candle.low < trailing_stop_loss:
                EXIT_candle = candle
                self.EXIT = trailing_stop_loss
                self.trade_status = TradeStatus.CLOSED
                break

            if candle.high > high:
                high = candle.high
                new_stop_loss = True
                trailing_stop_loss = high * (1 - self.settings.trailing_stop)

            if new_stop_loss and candle.low < trailing_stop_loss:
                EXIT_candle = candle
                self.EXIT = trailing_stop_loss
                self.trade_status = TradeStatus.CLOSED
                break

        if EXIT_candle is None:
            self.trade_status = TradeStatus.OPEN
        else:
            self.EXIT_date = EXIT_candle.name.date()

    def build_trade_dictionary(self):
        self.trade_dictionary = {
            "ticker": self.ticker,
            "TC_date": self.TC_date,
            "ENTRY": self.ENTRY,
            "R_ENTRY": self.R_ENTRY,
            "ENTRY_date": self.ENTRY_date,
            "SL": self.SL,
            "TP": self.TP,
            "TP_date": self.TP_date,
            "EXIT": self.EXIT,
            "EXIT_date": self.EXIT_date,
            "trade_status": self.trade_status,
            "outcome_status": self.outcome_status,

            "ENTRY_SL": self.ENTRY_SL,
            "R_ENTRY_SL": self.R_ENTRY_SL,

            "TP_ENTRY": self.TP_ENTRY,
            "TP_R_ENTRY": self.TP_R_ENTRY,

            "TP_TC_HIGH_RATIO": self.TP_TC_HIGH_RATIO,

            "PL": self.PL,
            "R_PL": self.R_PL,

            "SHARES_TO_BUY": self.SHARES_TO_BUY,
            "PRED_INVESTMENT": self.PRED_INVESTMENT,
            "INVESTMENT": self.INVESTMENT,
            "DELTA_INVESTMENT": self.DELTA_INVESTMENT,

            "PRED_OUTCOME": self.PRED_OUTCOME,
            "OUTCOME": self.OUTCOME,
            "TOTAL_DAYS": self.TOTAL_DAYS,
            "REQ_CAPITAL": self.REQ_CAPITAL,

            "VOLATILITY": self.VOLATILITY,
        }
