from ._base import FinancialStatementBase

class CashFlow(FinancialStatementBase):
    _attributes = [
        "operating_cashflow",
        "depreciation",
        "amortization",
    ]

    _attributes_with_setters = [
        "capital_expenditure",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def coa_items(self):
        return {
            "OTLO": self.set_operating_cashflow,
            "SDED": self.set_depreciation,
            "SAMT": self.set_amortization,
            "SCEX": self.set_capital_expenditure,
        }

    @property
    def free_cashflow(self):
        return self.operating_cashflow - self.capital_expenditure