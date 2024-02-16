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
    def earnings_per_share(self):
        return self.income.net_income / self.balance.total_outstanding_shares_common_stock

    @property
    def price_to_earnings(self):
        return self.price / self.earnings_per_share

    @property
    def ebitda_margin(self):
        return self.ebitda / self.income.revenue * 100

    # NOTE: This should include the average of total assets from the last two years - not implemented yet
    @property
    def return_on_assets(self):
        return self.income.net_income / self.balance.total_assets * 100

    @property
    def peg_trailing_3y(self):
        try:
            result = self.trailing_pe / \
                ((self.earnings_per_share[0] /
                 self.earnings_per_share[3])**(1/3.0) - 1) / 100
        except:
            result = np.nan
        return result
