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

from .enums import ChartEnum, TradeStatus, TradeOutcome
from .tradeSettings import TradeSettings
from .decorators import ignore_trade_exceptions, check_trade_status
from .common import (
    calc_highest_body_price,
    calc_lowest_body_price,
    find_daily_candle,
    find_last_high,
)


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

        self.trade_status = TradeStatus.UNKNOWN
        self.settings = settings if settings is not None else TradeSettings()

        self.outcome_status = TradeOutcome.NONE

    @ignore_trade_exceptions
    def execute_trade(self, pricing: pd.DataFrame):
        self.TC_index = pricing.index.get_loc(self.TC.name)

        self.setup_TP(
            pricing=pricing,
            max_candles=self.settings.max_CandleDist_TP_ENTRY,
            min_ratio_high_to_ref_candle=self.settings.min_ratio_high_to_ref_candle,
            max_drawdown_ratio_after_new_high=self.settings.max_drawdown_ratio_after_new_high,
        )

        self.calculate_LOW_between_ENTRY_and_TP(
            pricing=pricing,
            ENTRY_index=self.TC_index,
            TP_index=self.TP_index
        )

        self.check_TP_TC_to_LOW_RATIO()

        self.check_PL_RATIOS()

        self.calc_R_ENTRY(pricing)

        self.check_min_volatility()

        self.calc_EXIT(pricing, self.ENTRY_date)

        self.determine_trade_outcome()

    def determine_trade_outcome(self):
        if self.trade_status == TradeStatus.CLOSED:
            if self.EXIT > self.R_ENTRY:
                self.outcome_status = TradeOutcome.WIN
            elif self.EXIT < self.R_ENTRY:
                self.outcome_status = TradeOutcome.LOSS
        else:
            self.outcome_status = TradeOutcome.NONE

    @check_trade_status
    def check_PL_RATIOS(self):

        if self.settings.min_PL is not None and self.PL < self.settings.min_PL:
            self.trade_status = TradeStatus.PL_TOO_SMALL

        if self.settings.max_PL is not None and self.PL > self.settings.max_PL:
            self.trade_status = TradeStatus.PL_TOO_LARGE

    @check_trade_status
    def setup_TP(self,
                 pricing: pd.DataFrame,
                 max_candles: int = 10,
                 min_ratio_high_to_ref_candle: float = 1.0,
                 max_drawdown_ratio_after_new_high: float = 1.0,
                 ):

        if self.settings.TP_strategy == ChartEnum.LAST_HIGH:
            TP, TP_index = find_last_high(
                pricing=pricing,
                ref_candle_index=self.TC_index,
                max_candles=max_candles,
                min_ratio_high_to_ref_candle=min_ratio_high_to_ref_candle,
                max_drawdown_ratio_after_new_high=max_drawdown_ratio_after_new_high,
            )
        else:
            raise NotImplementedError(
                f"Invalid take profit setting {self.settings.TP_strategy}")

        if TP is None:
            self.trade_status = TradeStatus.TP_NOT_FOUND
            return
        elif TP / self.TC.high < min_ratio_high_to_ref_candle:
            self.trade_status = TradeStatus.TP_TC_HIGH_RATIO_TOO_SMALL
            return

        TP_date = self.calc_TP_date(
            pricing, TP_index, TP)

        self.TP = TP
        self.TP_date = TP_date
        self.TP_index = TP_index
        self.max_TP_B = calc_highest_body_price(
            pricing.iloc[self.TP_index])

    def calc_TP_date(self, pricing: pd.DataFrame, target_candle_index, take_profit):

        candle, take_profit = find_daily_candle(
            ticker=self.ticker,
            pricing=pricing,
            candle_index=target_candle_index,
            target_price=take_profit
        )

        return candle.name.date()

    @check_trade_status
    def calculate_LOW_between_ENTRY_and_TP(self, pricing, ENTRY_index, TP_index):

        self.low, self.LOW_index = self.find_last_low(
            pricing, ENTRY_index - TP_index)

        if self.settings.max_LOW_SL_to_ENTRY_RATIO is not None:
            if (self.ENTRY - self.low) / (self.ENTRY - self.SL) > self.settings.max_LOW_SL_to_ENTRY_RATIO:
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
                self.trade_status = TradeStatus.TP_B_TC_B_TO_LOW_RATIO_TOO_SMALL

    @check_trade_status
    def calc_R_ENTRY(self, pricing: pd.DataFrame):

        self.R_ENTRY = None
        self.ENTRY_date = None

        if self.TC_index != len(pricing)-1:
            min_date = pricing.index[self.TC_index+1].date()
            while True:
                R_ENTRY_candle, self.R_ENTRY = find_daily_candle(
                    ticker=self.ticker,
                    pricing=pricing,
                    candle_index=self.TC_index+1,
                    target_price=self.ENTRY,
                    min_date=min_date
                )

                self.ENTRY_date = R_ENTRY_candle.name.date() if R_ENTRY_candle is not None else None

                if R_ENTRY_candle is None:
                    break

                limit_ratio = (self.R_ENTRY - self.SL) / (self.ENTRY - self.SL)

                if self.settings.loss_limit is not None and limit_ratio > self.settings.loss_limit:
                    if (R_ENTRY_candle.low - self.SL)/(self.ENTRY - self.SL) < self.settings.loss_limit:
                        self.R_ENTRY = self.settings.loss_limit * \
                            (self.ENTRY - self.SL) + self.SL
                        break
                    else:
                        min_date = R_ENTRY_candle.name.date() + pd.Timedelta(days=1)
                else:
                    break

            if self.R_ENTRY is None:
                self.trade_status = TradeStatus.NO_ENTRY_WITHIN_NEXT_INTERVAL

        if self.R_ENTRY is None:
            self.trade_status = TradeStatus.TO_BE_DETERMINED

    @check_trade_status
    def check_min_volatility(self):
        if self.VOLATILITY < self.settings.min_volatility:
            self.trade_status = TradeStatus.VOLATILITY_TOO_SMALL

    def calc_EXIT(self, pricing: pd.DataFrame, ENTRY_date):

        for candle_index in range(self.TC_index+1, len(pricing)):

            TP_EXIT_candle, _ = find_daily_candle(
                ticker=self.ticker,
                pricing=pricing,
                candle_index=candle_index,
                target_price=self.TP,
                min_date=ENTRY_date,
            )

            SL_EXIT_candle, SL_EXIT = find_daily_candle(
                ticker=self.ticker,
                pricing=pricing,
                candle_index=candle_index,
                target_price=self.SL,
                mode=np.less_equal,
                min_date=ENTRY_date,
            )

            if TP_EXIT_candle is None and SL_EXIT_candle is None:
                candle_to_choose = "none"
            elif TP_EXIT_candle is None:
                candle_to_choose = "SL"
            elif SL_EXIT_candle is None:
                candle_to_choose = "TP"
            elif TP_EXIT_candle.name.date() < SL_EXIT_candle.name.date():
                candle_to_choose = "TP"
            elif TP_EXIT_candle.name.date() > SL_EXIT_candle.name.date():
                candle_to_choose = "SL"
            else:
                if TP_EXIT_candle.open <= self.SL:
                    candle_to_choose = "SL"
                elif TP_EXIT_candle.open >= self.TP:
                    candle_to_choose = "TP"
                else:
                    candle_to_choose = "ambiguous"

            if candle_to_choose == "TP":
                EXIT_candle = TP_EXIT_candle
                self.EXIT = self.TP
                self.trade_status = TradeStatus.CLOSED
            elif candle_to_choose == "SL":
                EXIT_candle = SL_EXIT_candle
                self.EXIT = SL_EXIT
                self.trade_status = TradeStatus.CLOSED
            elif candle_to_choose == "ambiguous":
                EXIT_candle = TP_EXIT_candle
                self.trade_status = TradeStatus.AMBIGUOUS_EXIT_DATE

            if candle_to_choose != "none":
                self.EXIT_date = EXIT_candle.name.date()
                break
            else:
                EXIT_candle = None

        if EXIT_candle is None:
            self.trade_status = TradeStatus.OPEN

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

    @property
    def ENTRY_SL(self):
        return self.property_subtraction(self.ENTRY, self.SL)

    @property
    def R_ENTRY_SL(self):
        return self.property_subtraction(self.R_ENTRY, self.SL)

    @property
    def TP_ENTRY(self):
        return self.property_subtraction(self.TP, self.ENTRY)

    @property
    def TP_R_ENTRY(self):
        return self.property_subtraction(self.TP, self.R_ENTRY)

    @property
    def PRED_INVESTMENT(self):
        return self.property_division(self.ENTRY, self.ENTRY_SL)

    @property
    def INVESTMENT(self):
        return self.property_division(self.R_ENTRY, self.ENTRY_SL)

    @property
    def DELTA_INVESTMENT(self):
        return self.property_subtraction(self.INVESTMENT, self.PRED_INVESTMENT)

    @property
    def EXIT_ENTRY(self):
        return self.property_subtraction(self.EXIT, self.ENTRY)

    @property
    def EXIT_R_ENTRY(self):
        return self.property_subtraction(self.EXIT, self.R_ENTRY)

    @property
    def PRED_OUTCOME(self):
        return self.property_division(self.EXIT_ENTRY, self.ENTRY_SL)

    @property
    def OUTCOME(self):
        return self.property_division(self.EXIT_R_ENTRY, self.ENTRY_SL)

    @property
    def PL(self):
        return self.property_division(self.TP_ENTRY, self.ENTRY_SL)

    @property
    def R_PL(self):
        return self.property_division(self.TP_R_ENTRY, self.R_ENTRY_SL)

    @property
    def SHARES_TO_BUY(self):
        return self.property_division(1, self.ENTRY_SL)

    @property
    def TOTAL_DAYS(self):
        date_diff = self.property_subtraction(self.EXIT_date, self.ENTRY_date)
        if date_diff is None:
            return None
        else:
            return date_diff.days + 1

    @property
    def REQ_CAPITAL(self):
        return self.property_multiplication(self.INVESTMENT, self.TOTAL_DAYS)

    @property
    def VOLATILITY(self):
        return self.property_division(self.ENTRY_SL, self.ENTRY)

    @property
    def TP_TC_HIGH_RATIO(self):
        ratio = self.property_division(self.TP, self.TC.high)
        return self.property_subtraction(ratio, 1)

    def to_json(self):
        return {
            "ticker": self.ticker,
            "TC_date": self.TC_date.isoformat(),
            "ENTRY": self.ENTRY,
            "R_ENTRY": self.R_ENTRY,
            "ENTRY_date": self.ENTRY_date.isoformat(),
            "SL": self.SL,
            "TP": self.TP,
            "TP_date": self.TP_date.isoformat(),
            "EXIT": self.EXIT,
            "EXIT_date": self.EXIT_date.isoformat(),
            "trade_status": self.trade_status.value,
            "outcome": self.outcome_status.value,
            "settings": self.settings.to_json()
        }

    @classmethod
    def init_from_json(cls, json):
        trade = cls(
            ticker=json["ticker"],
            trigger_candle=None,
            settings=TradeSettings.from_json(json["settings"])
        )

        trade.TC_date = dt.date.fromisoformat(json["TC_date"])
        trade.ENTRY = json["ENTRY"]
        trade.R_ENTRY = json["R_ENTRY"]
        trade.ENTRY_date = dt.date.fromisoformat(json["ENTRY_date"])
        trade.SL = json["SL"]
        trade.TP = json["TP"]
        trade.TP_date = dt.date.fromisoformat(json["TP_date"])
        trade.EXIT = json["EXIT"]
        trade.EXIT_date = dt.date.fromisoformat(json["EXIT_date"])
        trade.trade_status = TradeStatus(json["trade_status"])
        trade.outcome_status = TradeOutcome(json["outcome"])

        return trade

    def property_subtraction(self, a, b):
        if a is None or b is None:
            return None
        else:
            return a - b

    def property_multiplication(self, a, b):
        if a is None or b is None:
            return None
        else:
            return a * b

    def property_division(self, a, b):
        if a is None or b is None:
            return None
        else:
            return a / b
