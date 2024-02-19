import numpy as np


class FinancialStatementBase:
    def __init__(self, coa_type=None):
        if coa_type is None:
            self.coa_type: str = "NotDefined"
        else:
            self.coa_type: str = coa_type

        self.fiscal_years = []
        self.fiscal_year_end_dates = []
        self.reporting_dates = []

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        def property_factory(attr, setter=False):
            def getter(self):
                return getattr(self, "_" + attr)

            if setter:
                def func(self, value):
                    setattr(self, "_" + attr, np.nan_to_num(value, nan=0))

            else:
                def func(self, value):
                    setattr(self, "_" + attr, value)

            return property(getter), func

        if "_attributes_with_setters" in cls.__dict__:
            _attributes_with_setters = cls._attributes_with_setters
        else:
            _attributes_with_setters = []

        _attributes = cls._attributes + _attributes_with_setters

        for attr in _attributes:
            getter, setter = property_factory(
                attr, attr in _attributes_with_setters)

            setattr(cls, attr, getter)
            setattr(cls, "set_" + attr, setter)

        for attr in cls._attributes:
            setattr(cls, "_" + attr, np.array([np.nan]))
