from __future__ import annotations

import pandas as pd
import datetime as dt

from dataclasses import dataclass, field
from beartype.typing import List


@dataclass(kw_only=True)
class IncomeStatementBase:
    pass


@dataclass(kw_only=True)
class BalanceSheetBase:
    pass


@dataclass(kw_only=True)
class CashFlowStatementBase:
    pass


@dataclass(kw_only=True)
class ContractInfoBase:
    ticker: str


@dataclass(kw_only=True)
class FinancialStatementInfoBase:
    coa_type: str = "NotDefined"
    fiscal_years: List[int] = field(default_factory=list)
    fiscal_year_end_dates: List[dt.date] = field(default_factory=list)


@dataclass(kw_only=True)
class FinancialStatementBase(FinancialStatementInfoBase, IncomeStatementBase, BalanceSheetBase, CashFlowStatementBase):
    pass


@dataclass(kw_only=True)
class Contract(FinancialStatementBase, ContractInfoBase):
    pass


@dataclass(kw_only=True)
class FinancialStatement(ContractInfoBase, FinancialStatementBase):
    pass


@dataclass(kw_only=True)
class IncomeStatement(FinancialStatementInfoBase, IncomeStatementBase):
    pass


@dataclass(kw_only=True)
class BalanceSheet(FinancialStatementInfoBase, BalanceSheetBase):
    pass


@dataclass(kw_only=True)
class CashFlowStatement(FinancialStatementInfoBase, CashFlowStatementBase):
    pass
