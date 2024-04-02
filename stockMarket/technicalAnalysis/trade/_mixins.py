import pandas as pd
import datetime as dt

from beartype.typing import Any, Dict

from .common import calc_highest_body_price, calc_lowest_body_price
from .enums import TradeOutcome, TradeStatus
from .tradeSettings import TradeSettings


class PropertyMixin:
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


class JSONMixin:
    def to_json(self) -> Dict[str, Any]:
        return {
            "ticker": self.ticker,
            "TC_date": isoformat_or_none(self.TC_date),
            "ENTRY": self.ENTRY,
            "R_ENTRY": self.R_ENTRY,
            "ENTRY_date": isoformat_or_none(self.ENTRY_date),
            "SL": self.SL,
            "TP": self.TP,
            "TP_date": isoformat_or_none(self.TP_date),
            "EXIT": self.EXIT,
            "EXIT_date": isoformat_or_none(self.EXIT_date),
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

        trade.TC_date = fromisoformat_or_none(json["TC_date"])
        trade.ENTRY = json["ENTRY"]
        trade.R_ENTRY = json["R_ENTRY"]
        trade.ENTRY_date = fromisoformat_or_none(json["ENTRY_date"])
        trade.SL = json["SL"]
        trade.TP = json["TP"]
        trade.TP_date = fromisoformat_or_none(json["TP_date"])
        trade.EXIT = json["EXIT"]
        trade.EXIT_date = fromisoformat_or_none(json["EXIT_date"])
        trade.trade_status = TradeStatus(json["trade_status"])
        trade.outcome_status = TradeOutcome(json["outcome"])

        trade.build_trade_dictionary()

        return trade


def isoformat_or_none(date: pd.Timestamp):
    return date.isoformat() if date is not None else None


def fromisoformat_or_none(date: str):
    return dt.date.fromisoformat(date) if date is not None else None
