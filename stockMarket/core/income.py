import datetime as dt
import numpy as np

from dataclasses import dataclass, field
from beartype.typing import List

from .financialStatement import FinancialStatementBase


def init_income_class(coa_type, **kwargs):
    if coa_type == "Bank":
        return IncomeBank(coa_type=coa_type, **kwargs)
    elif coa_type == "Industry" or coa_type == "Insurance" or coa_type == "Utility":
        return IncomeIndustry(coa_type=coa_type, **kwargs)
    else:
        raise ValueError(f"coa_type {coa_type} is not valid")


@dataclass(kw_only=True)
class Income(FinancialStatementBase):
    net_income: np.ndarray[int, np.float64] = field(
        default_factory=lambda: np.ndarray(shape=0))

    @property
    def coa_items(self):
        return {
            "NINC": self.net_income,
        }

    @property
    def revenue_growth(self):
        return -np.diff(self.revenue) / self.revenue[1:] * 100

    @property
    def revenue_growth_all_time(self):
        growths = []
        for i in range(len(self.revenue)-1):
            growths.append(
                (self.revenue[i] - self.revenue[-1]) / self.revenue[-1] / (len(self.revenue) - i - 1) * 100)
        return np.array(growths)


@dataclass(kw_only=True)
class IncomeBank(Income):
    net_interest_income: np.ndarray[int, np.float64] = field(
        default_factory=lambda: np.ndarray(shape=0))
    non_interest_income: np.ndarray[int, np.float64] = field(
        default_factory=lambda: np.ndarray(shape=0))

    @property
    def revenue(self):
        return self.net_interest_income + self.non_interest_income

    @property
    def ebit(self):
        return np.array([np.nan] * len(self.net_interest_income))

    @property
    def coa_items(self):
        coa_items = super().coa_items
        coa_items["ENII"] = self.net_interest_income
        coa_items["SNII"] = self.non_interest_income
        return coa_items


@dataclass(kw_only=True)
class IncomeIndustry(Income):
    revenue: np.ndarray[int, np.float64] = field(
        default_factory=lambda: np.ndarray(shape=0))
    gross_profit: np.ndarray[int, np.float64] = field(
        default_factory=lambda: np.ndarray(shape=0))
    selling_general_admin: np.ndarray[int, np.float64] = field(
        default_factory=lambda: np.ndarray(shape=0))
    research_development: np.ndarray[int, np.float64] = field(
        default_factory=lambda: np.ndarray(shape=0))
    depreciation_amortization: np.ndarray[int, np.float64] = field(
        default_factory=lambda: np.ndarray(shape=0))
    total_operating_expenses: np.ndarray[int, np.float64] = field(
        default_factory=lambda: np.ndarray(shape=0))

    @property
    def ebit(self):
        return self.revenue - self.total_operating_expenses

    @property
    def coa_items(self):
        coa_items = super().coa_items
        coa_items["RTLR"] = self.revenue
        coa_items["SGRP"] = self.gross_profit
        coa_items["SSGA"] = self.selling_general_admin
        coa_items["ERAD"] = self.research_development
        coa_items["SDPR"] = self.depreciation_amortization
        coa_items["ETOE"] = self.total_operating_expenses
        return coa_items
