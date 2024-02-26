import numpy as np

from ._base import FinancialStatementBase


def init_income_class(coa_type, **kwargs):
    if coa_type == "Bank":
        return IncomeBank(coa_type=coa_type, **kwargs)
    elif coa_type == "Industry" or coa_type == "Insurance" or coa_type == "Utility":
        return IncomeIndustry(coa_type=coa_type, **kwargs)
    else:
        raise ValueError(f"coa_type {coa_type} is not valid")


class Income(FinancialStatementBase):
    _attributes = [
        "net_income",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def ebit_margin(self):
        return self.ebit / self.revenue * 100

    @property
    def netto_margin(self):
        return self.net_income / self.revenue * 100

    @property
    def coa_items(self):
        return {
            "NINC": self.set_net_income,
        }


class IncomeBank(Income):
    _attributes = [
        "interest_income",
        "non_interest_income",
    ]

    @property
    def revenue(self):
        return self.interest_income + self.non_interest_income

    @property
    def ebit(self):
        return np.array([np.nan] * len(self.interest_income))

    @property
    def coa_items(self):
        coa_items = super().coa_items
        coa_items["SIIB"] = self.set_interest_income
        coa_items["SNII"] = self.set_non_interest_income
        return coa_items


class IncomeIndustry(Income):
    _attributes = [
        "revenue",
        "gross_profit",
        "selling_general_admin",
        "total_operating_expenses",
    ]

    _attributes_with_setters = [
        "research_development",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.coa_type = "Industry"

    @property
    def ebit(self):
        return self.revenue - self.total_operating_expenses

    @property
    def coa_items(self):
        coa_items = super().coa_items
        coa_items["RTLR"] = self.set_revenue
        coa_items["SGRP"] = self.set_gross_profit
        coa_items["SSGA"] = self.set_selling_general_admin
        coa_items["ETOE"] = self.set_total_operating_expenses

        coa_items["ERAD"] = self.set_research_development

        return coa_items
