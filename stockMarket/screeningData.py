import pandas as pd
import numpy as np

from tqdm import tqdm


def setup_screener(type, id, title, multiplier, exception, year=0):
    if type == 'info':
        return InfoScreener(id, title, multiplier, exception)
    elif type == 'cashflow':
        return CashflowScreener(id, title, multiplier, exception, year=year)
    elif type == 'financials':
        return FinancialsScreener(id, title, multiplier, exception, year=year)
    elif type == 'balancesheet':
        return BalancesheetScreener(id, title, multiplier, exception, year=year)
    elif type == 'calendar':
        return CalendarScreener(id, title)
    else:
        raise ValueError("Type not supported")


class ThreeYearScreener:
    math = {
        'min': min,
        'max': max,
        'mean': np.mean,
        'sum': sum,
    }

    def __init__(self, id, title, type='financials', math_mode='min', multiplier=1, exception=None):
        self.id = id
        self.title = title
        self.multiplier = multiplier
        self.exception = exception

        if math_mode not in self.math:
            raise ValueError("Math not supported")
        else:
            self.math_mode = self.math[math_mode]

        self.screener1 = setup_screener(
            type, self.id, title, multiplier, exception, year=0)
        self.screener2 = setup_screener(
            type, self.id, title, multiplier, exception, year=1)
        self.screener3 = setup_screener(
            type, self.id, title, multiplier, exception, year=2)

    def set_data(self, tickers):
        self.data = {}

        self.screener1.set_data(tickers)
        self.screener2.set_data(tickers)
        self.screener3.set_data(tickers)

        for ticker in tickers:
            try:
                self.data[ticker] = self.math_mode([self.screener1.data[ticker],
                                                    self.screener2.data[ticker], self.screener3.data[ticker]])
            except Exception:
                self.data[ticker] = self.exception


class CalendarScreener:
    def __init__(self, id, title):
        self.id = id
        self.title = title

    def set_data(self, tickers):
        self.data = {}

        for ticker in tickers:
            try:
                _data = tickers[ticker].calendar[self.id]
            except (KeyError, AttributeError):
                _data = None

            if self.id == 'Earnings Date':
                if _data is None or len(_data) == 0:
                    self.data[ticker] = None
                elif len(_data) == 1:
                    self.data[ticker] = str(_data[0])
                else:
                    self.data[ticker] = "::".join(
                        [str(_data[0]), str(_data[1])])
            else:
                self.data[ticker] = _data


class InfoScreener:
    def __init__(self, id, title, multiplier=1, exception=None):
        self.id = id
        self.title = title
        self.multiplier = multiplier
        self.exception = exception
        self.year = 0

    def set_data(self, tickers):
        self.data = {}

        for ticker in tickers:
            try:
                self.data[ticker] = tickers[ticker].info[self.id] * \
                    self.multiplier
            except (KeyError, AttributeError):
                self.data[ticker] = self.exception


class CashflowScreener:
    def __init__(self, id, title, multiplier=1, exception=None, year=0):
        self.id = id
        self.title = title
        self.multiplier = multiplier
        self.exception = exception
        self.year = year

    def set_data(self, tickers):
        self.data = {}

        for ticker in tickers:
            try:
                self.data[ticker] = tickers[ticker].cashflow.loc[self.id].iloc[self.year] * self.multiplier
            except (KeyError, AttributeError):
                self.data[ticker] = self.exception


class FinancialsScreener:
    def __init__(self, id, title, multiplier=1, exception=None, year=0):
        self.id = id
        self.title = title
        self.multiplier = multiplier
        self.exception = exception
        self.year = year

    def set_data(self, tickers):
        self.data = {}
        for ticker in tickers:
            try:
                self.data[ticker] = tickers[ticker].financials.loc[self.id].iloc[self.year] * self.multiplier
            except (KeyError, AttributeError):
                self.data[ticker] = self.exception


class BalancesheetScreener:
    def __init__(self, id, title, multiplier=1, exception=None, year=0):
        self.id = id
        self.title = title
        self.multiplier = multiplier
        self.exception = exception
        self.year = year

    def set_data(self, tickers):
        self.data = {}

        for ticker in tickers:
            try:
                self.data[ticker] = tickers[ticker].balancesheet.loc[self.id].iloc[self.year] * self.multiplier
            except (KeyError, AttributeError):
                self.data[ticker] = self.exception


class GrowthScreener:
    types = ["cashflow", "financials", "balancesheet"]

    def __init__(self, id, title, type='financials', multiplier=1, exception=None, two_years=True):
        self.id = id
        self.title = title
        self.multiplier = multiplier
        self.exception = exception

        if two_years:
            self.end_year = 0
            self.start_year = 2
        else:
            self.end_year = 0
            self.start_year = 1

        self.end_screener = setup_screener(
            type, id, title, multiplier, exception, year=self.end_year)
        self.start_screener = setup_screener(
            type, id, title, multiplier, exception, year=self.start_year)

    def set_data(self, tickers):
        self.data = {}

        self.end_screener.set_data(tickers)
        self.start_screener.set_data(tickers)

        for ticker in tickers:
            try:
                self.data[ticker] = (self.end_screener.data[ticker] - self.start_screener.data[ticker]) / \
                    self.start_screener.data[ticker] * self.multiplier
            except Exception:
                self.data[ticker] = self.exception


class RelationToSumScreener:
    types = ["info", "cashflow", "financials", "balancesheet"]

    def __init__(self, type1, id1, type2, id2, title, multiplier=1, exception=None):
        self.type1 = type1
        self.id1 = id1
        self.type2 = type2
        self.id2 = id2
        self.title = title
        self.multiplier = multiplier
        self.exception = exception
        self.year = 0

        if self.type1 not in self.types or self.type2 not in self.types:
            raise ValueError("Type not supported")

        self.screener1 = setup_screener(
            self.type1, self.id1, title, multiplier, exception, year=self.year)
        self.screener2 = setup_screener(
            self.type2, self.id2, title, multiplier, exception, year=self.year)

    def set_data(self, tickers):
        self.data = {}

        self.screener1.set_data(tickers)
        self.screener2.set_data(tickers)

        for ticker in tickers:
            try:
                self.data[ticker] = self.screener1.data[ticker] / \
                    (self.screener1.data[ticker] +
                     self.screener2.data[ticker]) * self.multiplier
            except Exception:
                self.data[ticker] = self.exception
