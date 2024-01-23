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
    pass


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
