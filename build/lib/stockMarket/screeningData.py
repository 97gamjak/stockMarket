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


class CalendarScreener:
    def __init__(self, id, title):
        self.id = id
        self.title = title

    def set_data(self, tickers, disable_tqdm=False):
        self.data = {}

        if not disable_tqdm:
            print()
            print(f"Screening {self.title}...")
            print()

        for ticker in tqdm(tickers, disable=disable_tqdm):
            try:
                self.data[ticker] = tickers[ticker].calendar[self.id]
            except KeyError:
                self.data[ticker] = None


class InfoScreener:
    def __init__(self, id, title, multiplier=1, exception=None):
        self.id = id
        self.title = title
        self.multiplier = multiplier
        self.exception = exception
        self.year = 0

    def set_data(self, tickers, disable_tqdm=False):
        self.data = {}

        if not disable_tqdm:
            print()
            print(f"Screening {self.title}...")
            print()

        for ticker in tqdm(tickers, disable=disable_tqdm):
            try:
                self.data[ticker] = tickers[ticker].info[self.id] * \
                    self.multiplier
            except KeyError:
                self.data[ticker] = self.exception


class CashflowScreener:
    def __init__(self, id, title, multiplier=1, exception=None, year=0):
        self.id = id
        self.title = title
        self.multiplier = multiplier
        self.exception = exception
        self.year = year

    def set_data(self, tickers, disable_tqdm=False):
        self.data = {}

        if not disable_tqdm:
            print()
            print(f"Screening {self.title}...")
            print()

        for ticker in tqdm(tickers, disable=disable_tqdm):
            try:
                self.data[ticker] = tickers[ticker].cashflow.loc[self.id].iloc[self.year] * self.multiplier
            except KeyError:
                self.data[ticker] = self.exception


class FinancialsScreener:
    def __init__(self, id, title, multiplier=1, exception=None, year=0):
        self.id = id
        self.title = title
        self.multiplier = multiplier
        self.exception = exception
        self.year = year

    def set_data(self, tickers, disable_tqdm=False):
        self.data = {}
        if not disable_tqdm:
            print()
            print(f"Screening {self.title}...")
            print()

        for ticker in tqdm(tickers, disable=disable_tqdm):
            try:
                self.data[ticker] = tickers[ticker].financials.loc[self.id].iloc[self.year] * self.multiplier
            except KeyError:
                self.data[ticker] = self.exception


class BalancesheetScreener:
    def __init__(self, id, title, multiplier=1, exception=None, year=0):
        self.id = id
        self.title = title
        self.multiplier = multiplier
        self.exception = exception
        self.year = year

    def set_data(self, tickers, disable_tqdm=False):
        self.data = {}

        if not disable_tqdm:
            print()
            print(f"Screening {self.title}...")
            print()

        for ticker in tqdm(tickers, disable=disable_tqdm):
            try:
                self.data[ticker] = tickers[ticker].balancesheet.loc[self.id].iloc[self.year] * self.multiplier
            except KeyError:
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

    def set_data(self, tickers, disable_tqdm=False):
        self.data = {}

        if not disable_tqdm:
            print()
            print(f"Screening {self.title}...")
            print()

        self.end_screener.set_data(tickers, disable_tqdm=True)
        self.start_screener.set_data(tickers, disable_tqdm=True)

        for ticker in tqdm(tickers, disable=disable_tqdm):
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

    def set_data(self, tickers, disable_tqdm=False):
        self.data = {}

        if not disable_tqdm:
            print()
            print(f"Screening {self.title}...")
            print()

        self.screener1.set_data(tickers, disable_tqdm=True)
        self.screener2.set_data(tickers, disable_tqdm=True)

        for ticker in tqdm(tickers, disable=disable_tqdm):
            try:
                self.data[ticker] = self.screener1.data[ticker] / \
                    (self.screener1.data[ticker] +
                     self.screener2.data[ticker]) * self.multiplier
            except Exception:
                self.data[ticker] = self.exception
