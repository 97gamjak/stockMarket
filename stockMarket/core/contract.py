from __future__ import annotations

import pandas as pd
import numpy as np
import datetime as dt

from dataclasses import dataclass, field
from beartype.typing import Iterable

from .financialStatement import Income, BalanceSheet, CashFlow
from ._base import BaseMixin


def get_data_from(contract: Contract, values, date=None, years_back=0):

    if not isinstance(values, Iterable):
        return values

    if date is None:
        date = dt.date.today()

    if years_back > 0:
        date = date - pd.DateOffset(years=years_back)
        date = pd.to_datetime(date).date()

    i = 0
    while True:
        if contract.reporting_dates[i] < date:
            break
        else:
            i += 1

        if i == len(contract.reporting_dates):
            raise ValueError("No reporting dates found")

    return values[i]


@dataclass(kw_only=True)
class Contract(BaseMixin):
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

    full_pricing_info: pd.DataFrame | None = None

    def earnings_per_share_growth(self, years: int = 1):
        return self.growth(self.earnings_per_share, years)

    def revenue_per_share_growth(self, years: int = 1):
        return self.growth(self.revenue_per_share, years)

    def operating_cashflow_per_share_growth(self, years: int = 1):
        return self.growth(self.operating_cashflow_per_share, years)

    def free_cashflow_per_share_growth(self, years: int = 1):
        return self.growth(self.free_cashflow_per_share, years)

    def growth(self, value, years: int = 1):
        values = []
        for i, j in enumerate(range(years, len(value))):
            rate = value[i] / value[j]
            values.append((np.sign(rate)*(np.abs(rate))
                          ** (1/float(j)) - 1) * 100)

        return np.array(values)

    def get_price_by_date(self, date=None, years_back=0):
        if date is None:
            date = dt.date.today()

        date = date - pd.DateOffset(years=years_back)
        date = pd.to_datetime(date).date()

        return self.full_pricing_info[self.full_pricing_info.index <= date].iloc[-1].close

    def price_to_earnings(self, date=None, years_back=0):
        return self.get_price_by_date(date, years_back) / self.earnings_per_share

    def price_to_revenue(self, date=None, years_back=0):
        return self.get_price_by_date(date, years_back) / self.revenue_per_share

    def price_to_operating_cashflow(self, date=None, years_back=0):
        return self.get_price_by_date(date, years_back) / self.operating_cashflow_per_share

    def price_to_free_cashflow(self, date=None, years_back=0):
        return self.get_price_by_date(date, years_back) / self.free_cashflow_per_share

    def peg(self, growth_years, date=None, years_back=0):
        try:
            growth = self.earnings_per_share_growth(growth_years)
            result = (self.price_to_earnings(
                date, years_back)[:len(growth)] / growth)
        except:
            result = np.nan
        return result

    def prg(self, growth_years, date=None, years_back=0):

        try:
            growth = self.revenue_per_share_growth(growth_years)
            result = self.price_to_revenue(date, years_back)[
                :len(growth)] / growth
        except:
            result = np.nan
        return result

    def pocg(self, growth_years, date=None, years_back=0):
        try:
            growth = self.operating_cashflow_per_share_growth(growth_years)
            result = self.price_to_operating_cashflow(
                date, years_back)[:len(growth)] / growth
        except:
            result = np.nan
        return result

    def pfcg(self, growth_years, date=None, years_back=0):
        try:
            growth = self.free_cashflow_per_share_growth(growth_years)
            result = self.price_to_free_cashflow(date, years_back)[
                :len(growth)] / growth
        except:
            result = np.nan
        return result

    @property
    def ebitda(self):
        depreciation = np.nan_to_num(self.cashflow.depreciation)
        amortization = np.nan_to_num(self.cashflow.amortization)
        return self.income.ebit + depreciation + amortization

    @property
    def earnings_per_share(self):
        return self.income.net_income / self.balance.total_outstanding_shares_common_stock

    @property
    def revenue_per_share(self):
        return self.income.revenue / self.balance.total_outstanding_shares_common_stock

    @property
    def operating_cashflow_per_share(self):
        return self.cashflow.operating_cashflow / self.balance.total_outstanding_shares_common_stock

    @property
    def free_cashflow_per_share(self):
        return self.cashflow.free_cashflow / self.balance.total_outstanding_shares_common_stock

    @property
    def ebitda_margin(self):
        return self.ebitda / self.income.revenue * 100

    # NOTE: This should include the average of total assets from the last two years - not implemented yet
    @property
    def return_on_assets(self):
        return self.income.net_income / self.balance.total_assets * 100
