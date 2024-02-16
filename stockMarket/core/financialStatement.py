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
        default_factory=lambda: np.ndarray(shape=0)
    )
    total_debt: np.ndarray[int, np.float64] = field(
        default_factory=lambda: np.ndarray(shape=0)
    )
    total_liabilities: np.ndarray[int, np.float64] = field(
        default_factory=lambda: np.ndarray(shape=0)
    )
    total_assets: np.ndarray[int, np.float64] = field(
        default_factory=lambda: np.ndarray(shape=0)
    )
    goodwill: np.ndarray[int, np.float64] = field(
        default_factory=lambda: np.ndarray(shape=0)
    )
    total_outstanding_shares_common_stock: np.ndarray[int, np.float64] = field(
        default_factory=lambda: np.ndarray(shape=0)
    )
    current_portion_of_long_term_debt_and_capital_lease_obligations: np.ndarray[int, np.float64] = field(
        default_factory=lambda: np.ndarray(shape=0)
    )
    short_term_debt: np.ndarray[int, np.float64] = field(
        default_factory=lambda: np.ndarray(shape=0)
    )
    accrued_expenses: np.ndarray[int, np.float64] = field(
        default_factory=lambda: np.ndarray(shape=0)
    )
    total_long_term_debt: np.ndarray[int, np.float64] = field(
        default_factory=lambda: np.ndarray(shape=0)
    )
    cash_and_short_term_investments: np.ndarray[int, np.float64] = field(
        default_factory=lambda: np.ndarray(shape=0)
    )

    @property
    def equity_shareholders(self):
        return self.total_assets - self.total_liabilities

    @property
    def equity(self):
        return self.equity_shareholders

    @property
    def equity_ratio(self):
        return (self.equity_shareholders) / self.total_assets * 100

    @property
    def goodwill_ratio(self):
        goodwill = np.nan_to_num(self.goodwill, nan=0)
        return goodwill / self.equity * 100

    @property
    def total_short_term_debt(self):
        short_term_dept = np.nan_to_num(self.short_term_debt, nan=0)
        current_portion_of_long_term_debt_and_capital_lease_obligations = np.nan_to_num(
            self.current_portion_of_long_term_debt_and_capital_lease_obligations, nan=0)
        accrued_expenses = np.nan_to_num(self.accrued_expenses, nan=0)
        return short_term_dept + current_portion_of_long_term_debt_and_capital_lease_obligations + accrued_expenses

    @property
    def gearing(self):
        cash_and_short_term_investments = np.nan_to_num(
            self.cash_and_short_term_investments, nan=0)
        total_long_term_debt = np.nan_to_num(self.total_long_term_debt, nan=0)
        return (self.total_short_term_debt + total_long_term_debt - cash_and_short_term_investments)/self.equity * 100

    @property
    def coa_items(self):
        return {
            "QTLE": self.common_stocK_equity,
            "LTLL": self.total_liabilities,
            "STLD": self.total_debt,
            "ATOT": self.total_assets,
            "AGWI": self.goodwill,
            "QTCO": self.total_outstanding_shares_common_stock,
            "LCLD": self.current_portion_of_long_term_debt_and_capital_lease_obligations,
            "LSTD": self.short_term_debt,
            "LAEX": self.accrued_expenses,
            "LTTD": self.total_long_term_debt,
            "SCSI": self.cash_and_short_term_investments,
        }


class _BalanceSheetPropertiesMixin:
    @property
    def goodwill_ratio(self):
        return self.balance.goodwill_ratio

    @property
    def equity_ratio(self):
        return self.balance.equity_ratio

    @property
    def gearing(self):
        return self.balance.gearing


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
