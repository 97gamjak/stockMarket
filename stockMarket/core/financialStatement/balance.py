import numpy as np

from ._base import FinancialStatementBase


class BalanceSheet(FinancialStatementBase):
    _attributes = [
        "equity",
        "total_liabilities",
        "total_current_liabilities",
        "total_assets",
        "total_outstanding_shares_common_stock",
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
        "intangible_assets",
    ]

    _attributes_to_assert = [
        "book_value_per_share_assert",
        "total_debt_assert",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def equity_ratio(self):
        return (self.equity) / self.total_assets * 100

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
    def book_value(self):
        return self.equity - self.goodwill - self.intangible_assets

    @property
    def book_value_per_share(self):
        return self.book_value / self.total_outstanding_shares_common_stock

    @property
    def assert_balance(self):
        assert np.allclose(self.book_value_per_share, self.book_value_per_share_assert,
                           rtol=1), f"Book value per share: {self.book_value_per_share} != {self.book_value_per_share_assert}"

        assert np.allclose(self.total_debt, self.total_debt_assert,
                           rtol=1), f"Total debt: {self.total_debt} != {self.total_debt_assert}"

        assert np.allclose(self.equity, self.total_assets - self.total_liabilities,
                           rtol=1), f"Equity: {self.equity} != {self.total_assets - self.total_liabilities}"

        print("Balance sheet assertion passed")

    @property
    def coa_items(self):
        return {
            "QTLE": self.set_equity,
            "LTLL": self.set_total_liabilities,
            "LTCL": self.set_total_current_liabilities,
            "ATOT": self.set_total_assets,
            "QTCO": self.set_total_outstanding_shares_common_stock,
            "AGWI": self.set_goodwill,
            "LSTD": self.set_short_term_debt,
            "LCLD": self.set_current_portion_of_long_term_debt_and_capital_lease_obligations,
            "LAEX": self.set_accrued_expenses,
            "LTTD": self.set_total_long_term_debt,
            "ATRC": self.set_total_receivables_net,
            "AITL": self.set_total_inventory,
            "SOCA": self.set_other_current_assets,
            "APPY": self.set_prepaid_expenses,
            "ACSH": self.set_cash,
            "ACAE": self.set_cash_equivalents,
            "ASTI": self.set_short_term_investments,
            "AINT": self.set_intangible_assets,

            "STBP": self.set_book_value_per_share_assert,
            "STLD": self.set_total_debt_assert,
        }
