from .financialStatement.income import IncomeBank, IncomeIndustry
from .financialStatement import Income, BalanceSheet, CashFlow
from .financialStatement._base import FinancialStatementBase


class BaseMixin:
    classes = [Income, IncomeBank, IncomeIndustry,
               BalanceSheet, CashFlow, FinancialStatementBase]

    def __init_subclass__(cls) -> None:
        _attributes, _attributes_with_setters, properties = cls.get_attributes()

        def property_factory(c, attr):
            if c in [Income, IncomeBank, IncomeIndustry, FinancialStatementBase]:
                def getter(self):
                    return getattr(self.income, attr)
            elif c in [BalanceSheet]:
                def getter(self):
                    return getattr(self.balance, attr)
            elif c in [CashFlow]:
                def getter(self):
                    return getattr(self.cashflow, attr)

            return property(getter)

        for c in cls.classes:
            attributes_to_set = _attributes[c] + \
                _attributes_with_setters[c] + properties[c]
            for attr in attributes_to_set:
                setattr(cls, attr, property_factory(c, attr))

    @classmethod
    def get_attributes(cls):
        _attributes = {}
        _attributes_with_setters = {}
        _properties = {}
        for c in cls.classes:
            if "_attributes" not in c.__dict__:
                c._attributes = []
            else:
                _attributes[c] = c._attributes

            if "_attributes_with_setters" in c.__dict__:
                _attributes_with_setters[c] = c._attributes_with_setters
            else:
                _attributes_with_setters[c] = []

            _properties[c] = [item for item in c.__dict__
                              if isinstance(c.__dict__[item], property)]

        return _attributes, _attributes_with_setters, _properties
