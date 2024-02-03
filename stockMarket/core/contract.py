from __future__ import annotations

import pandas as pd
import numpy as np
import datetime as dt

from dataclasses import dataclass, field

from .income import Income, _IncomePropertiesMixin
from .financialStatement import BalanceSheet, CashFlow, _BalanceSheetPropertiesMixin, _CashFlowPropertiesMixin


@dataclass(kw_only=True)
class Contract(
        _IncomePropertiesMixin,
        _BalanceSheetPropertiesMixin,
        _CashFlowPropertiesMixin
):
    ticker: str
    exchange: str = ""
    currency: str = ""
    long_name: str = ""
    sector: str = ""

    price: float = np.nan
    trailing_pe: float = np.nan
    forward_pe: float = np.nan
    market_cap: float = np.nan
    dividend_yield: float = np.nan
    payout_ratio: float = np.nan

    income: Income = field(default_factory=Income)
    balance: BalanceSheet = field(default_factory=BalanceSheet)
    cashflow: CashFlow = field(default_factory=CashFlow)

    earnings_date: dt.datetime | pd.NaT = pd.NaT
    ex_dividend_date: dt.datetime | pd.NaT = pd.NaT
    pays_dividend: bool = False

    @property
    def ebitda(self):
        depreciation = np.nan_to_num(self.cashflow.depreciation)
        amortization = np.nan_to_num(self.cashflow.amortization)
        return self.income.ebit + depreciation + amortization

    @property
    def ebitda_margin(self):
        return self.ebitda / self.income.revenue * 100
