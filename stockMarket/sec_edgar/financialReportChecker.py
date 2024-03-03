import pandas as pd
import numpy as np
import datetime as dt
import glob

from pathlib import Path

from stockMarket.api import populate_contracts
from stockMarket import __data_path__


class FinancialReportChecker:
    edgar_path = __data_path__ / 'sec-edgar-filings'

    def __init__(self, ticker):
        self.ticker = ticker
        self.contract = populate_contracts(ticker)[0]
        self.filenames = glob.glob(
            str(self.edgar_path / ticker / '10-K') + '/*.csv')
        self.filename = self.filenames[0]

    def check_data(self):
        if not Path(self.filename).exists():
            raise FileNotFoundError(
                f'{self.ticker} is not found in the sec-edgar-filings directory')

        df = pd.read_csv(self.filename)

        if df.empty:
            raise ValueError(f'{self.ticker} has no financial data')

        self.ref_dates = self.contract.fiscal_year_end_dates
        self.dates = df["endDate"].values[::-1]
        self.ref_revenue = self.contract.revenue
        self.revenue = df['revenue'].values[::-1]

        self.new_revenue = []
        self.new_dates = []
        for ref_date in self.ref_dates:
            for i, date in enumerate(self.dates):
                if pd.Timestamp(date).year == pd.Timestamp(ref_date).year:
                    self.new_revenue.append(self.revenue[i])
                    self.new_dates.append(date)
                    break

        self.revenue = np.array(self.new_revenue)
        self.dates = np.array(self.new_dates)

        self.revenue = self.revenue[:len(self.ref_revenue)]

        return np.allclose(self.ref_revenue[:len(self.revenue)], self.revenue)
