import datetime as dt

from dataclasses import dataclass, field
from beartype.typing import List

from .financialStatement import FinancialStatementBase


def init_income_class(coa_type, **kwargs):
    if coa_type == "Bank":
        return IncomeBank(coa_type=coa_type, **kwargs)
    elif coa_type == "Industry":
        return IncomeIndustry(coa_type=coa_type, **kwargs)
    else:
        raise ValueError(f"coa_type {coa_type} is not valid")


@dataclass(kw_only=True)
class Income(FinancialStatementBase):
    revenue: List[float] = field(default_factory=list)

    @property
    def xml_ids(self):
        return {}


@dataclass(kw_only=True)
class IncomeBank(Income):
    @property
    def xml_ids(self):
        return super().xml_ids


@dataclass(kw_only=True)
class IncomeIndustry(Income):
    @property
    def xml_ids(self):
        xml_ids = super().xml_ids
        xml_ids["Total Revenue"] = self.revenue
        return xml_ids
