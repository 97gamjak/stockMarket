import datetime as dt

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
    operating_cashflow: List[float] = field(default_factory=list)

    @property
    def coa_items(self):
        return {
            "OTLO": self.operating_cashflow,
        }
