import datetime as dt
import numpy as np

from dataclasses import dataclass, field
from beartype.typing import List


@dataclass(kw_only=True)
class FinancialStatementBase:
    coa_type: str = "NotDefined"
    fiscal_years: List[int] = field(default_factory=list)
    fiscal_year_end_dates: List[dt.date] = field(default_factory=list)


@dataclass(kw_only=True)
class BalanceSheet(FinancialStatementBase):
    common_stocK_equity: np.ndarray[int, np.float64] = field(
        default_factory=lambda: np.ndarray(shape=0))
    total_debt: np.ndarray[int, np.float64] = field(
        default_factory=lambda: np.ndarray(shape=0))
    total_liabilities: np.ndarray[int, np.float64] = field(
        default_factory=lambda: np.ndarray(shape=0))
    total_assets: np.ndarray[int, np.float64] = field(
        default_factory=lambda: np.ndarray(shape=0))

    @property
    def equity_ratio(self):
        return (self.total_assets - self.total_liabilities) / self.total_assets * 100

    @property
    def coa_items(self):
        return {
            "QTLE": self.common_stocK_equity,
            "LTLL": self.total_liabilities,
            "STLD": self.total_debt,
            "ATOT": self.total_assets,
        }


class _BalanceSheetPropertiesMixin:
    @property
    def equity_ratio(self):
        return self.balance.equity_ratio


@dataclass(kw_only=True)
class CashFlow(FinancialStatementBase):
    operating_cashflow: np.ndarray[int, np.float64] = field(
        default_factory=lambda: np.ndarray(shape=0))
    depreciation: np.ndarray[int, np.float64] = field(
        default_factory=lambda: np.ndarray(shape=0))
    amortization: np.ndarray[int, np.float64] = field(
        default_factory=lambda: np.ndarray(shape=0))

    @property
    def coa_items(self):
        return {
            "OTLO": self.operating_cashflow,
            "SDED": self.depreciation,
            "SAMT": self.amortization,
        }


class _CashFlowPropertiesMixin:
    @property
    def operating_cashflow(self):
        return self.cashflow.operating_cashflow
