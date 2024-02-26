import numpy as np

from ._base import FinancialStatementBase


class BalanceSheet(FinancialStatementBase):
    _attributes = [
        "common_stocK_equity",
        "total_liabilities",
        "total_current_liabilities",
        "total_assets",
        "total_outstanding_shares_common_stock",
        "book_value_per_share",
    ]

    _attributes_with_setters = [
        "goodwill",
        "current_portion_of_long_term_debt_and_capital_lease_obligations",
        "short_term_debt",
        "accrued_expenses",
        "total_long_term_debt",
        "total_receivables_net",
        "total_inventory",
        "other_current_assets",
        "prepaid_expenses",
        "cash",
        "cash_equivalents",
        "short_term_investments",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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
        return self.goodwill / self.equity * 100

    @property
    def total_short_term_debt(self):
        return self.short_term_debt + self.current_portion_of_long_term_debt_and_capital_lease_obligations

    @property
    def total_current_assets(self):
        return self.cash_and_short_term_investments + self.total_receivables_net + self.total_inventory + self.other_current_assets + self.prepaid_expenses

    @property
    def total_debt(self):
        return self.total_short_term_debt + self.total_long_term_debt

    @property
    def gearing(self):
        return (self.total_debt - self.cash_and_short_term_investments)/self.equity * 100

    @property
    def total_non_current_assets(self):
        return self.total_assets - self.total_current_assets

    @property
    def asset_coverage_ratio(self):
        return (self.equity + self.total_long_term_debt) / self.total_non_current_assets * 100

    @property
    def third_order_liquidity(self):
        total_current_liabilities = []
        for debt in self.total_current_liabilities:
            if debt == 0:
                total_current_liabilities.append(1e-10)
            else:
                total_current_liabilities.append(debt)
        total_current_liabilities = np.array(total_current_liabilities)

        return self.total_current_assets / total_current_liabilities * 100

    @property
    def cash_and_short_term_investments(self):
        return self.cash + self.cash_equivalents + self.short_term_investments

    @property
    def coa_items(self):
        return {
            "QTLE": self.set_common_stocK_equity,
            "LTLL": self.set_total_liabilities,
            "LTCL": self.set_total_current_liabilities,
            "STLD": self.set_total_debt,
            "ATOT": self.set_total_assets,
            "QTCO": self.set_total_outstanding_shares_common_stock,
            "AGWI": self.set_goodwill,
            "LSTD": self.set_short_term_debt,
            "LCLD": self.set_current_portion_of_long_term_debt_and_capital_lease_obligations,
            "LAEX": self.set_accrued_expenses,
            "LTTD": self.set_total_long_term_debt,
            "STBP": self.set_book_value_per_share,
            "ATRC": self.set_total_receivables_net,
            "AITL": self.set_total_inventory,
            "SOCA": self.set_other_current_assets,
            "APPY": self.set_prepaid_expenses,
            "ACSH": self.set_cash,
            "ACAE": self.set_cash_equivalents,
            "ASTI": self.set_short_term_investments,
        }
