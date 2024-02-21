from ._base import FinancialStatementBase


class BalanceSheet(FinancialStatementBase):
    _attributes = [
        "common_stocK_equity",
        "total_debt",
        "total_liabilities",
        "total_current_assets",
        "total_assets",
        "total_outstanding_shares_common_stock",
        "cash_and_short_term_investments",
        "book_value_per_share",
    ]

    _attributes_with_setters = [
        "goodwill",
        "current_portion_of_long_term_debt_and_capital_lease_obligations",
        "short_term_debt",
        "accrued_expenses",
        "total_long_term_debt",
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
        return self.short_term_debt + self.current_portion_of_long_term_debt_and_capital_lease_obligations + self.accrued_expenses

    @property
    def gearing(self):
        return (self.total_short_term_debt + self.total_long_term_debt - self.cash_and_short_term_investments)/self.equity * 100

    @property
    def total_non_current_assets(self):
        return self.total_assets - self.total_current_assets

    @property
    def asset_coverage_ratio(self):
        return (self.equity + self.total_long_term_debt) / self.total_non_current_assets * 100

    @property
    def coa_items(self):
        return {
            "QTLE": self.set_common_stocK_equity,
            "LTLL": self.set_total_liabilities,
            "STLD": self.set_total_debt,
            "ATCA": self.set_total_current_assets,
            "ATOT": self.set_total_assets,
            "QTCO": self.set_total_outstanding_shares_common_stock,
            "SCSI": self.set_cash_and_short_term_investments,
            "AGWI": self.set_goodwill,
            "LSTD": self.set_short_term_debt,
            "LCLD": self.set_current_portion_of_long_term_debt_and_capital_lease_obligations,
            "LAEX": self.set_accrued_expenses,
            "LTTD": self.set_total_long_term_debt,
            "STBP": self.set_book_value_per_share,
        }
