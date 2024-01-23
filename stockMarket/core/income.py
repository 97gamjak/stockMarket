import datetime as dt

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
    net_income: List[float] = field(default_factory=list)

    @property
    def coa_items(self):
        return {
            "NINC": self.net_income,
        }


@dataclass(kw_only=True)
class IncomeBank(Income):
    net_interest_income: List[float] = field(default_factory=list)
    non_interest_income: List[float] = field(default_factory=list)

    @property
    def revenue(self):
        return [sum(x) for x in zip(self.net_interest_income, self.non_interest_income)]

    @revenue.setter
    def revenue(self, value):
        self.revenue = value

    @property
    def coa_items(self):
        coa_items = super().coa_items
        coa_items["ENII"] = self.net_interest_income
        coa_items["SNII"] = self.non_interest_income
        return coa_items


@dataclass(kw_only=True)
class IncomeIndustry(Income):
    revenue: List[float] = field(default_factory=list)

    @property
    def coa_items(self):
        coa_items = super().coa_items
        coa_items["RTLR"] = self.revenue
        return coa_items
