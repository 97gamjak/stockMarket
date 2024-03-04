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
        self.contract = populate_contracts(ticker.replace("-", "."))[0]
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

        self.relative_revenue = self.revenue / self.revenue[0]
        self.relative_revenue_to_ref = self.ref_revenue / self.ref_revenue[0]

        if not all(0.2 < self.relative_revenue) and not all(self.relative_revenue < 5.0):
            raise ValueError(f'{self.ticker} has inconsistent revenue data')
        elif not all(0.2 < self.relative_revenue_to_ref) and not all(self.relative_revenue_to_ref < 5.0):
            raise ValueError(f'{self.ticker} has inconsistent revenue data')

        self.wrong_data = {}
        for i, ref_date in enumerate(self.ref_dates):
            for j, date in enumerate(self.dates):
                if pd.Timestamp(date).year == pd.Timestamp(ref_date).year:
                    if self.revenue[j] < self.ref_revenue[i] and self.revenue[j] / self.ref_revenue[i] < 0.95:
                        self.wrong_data[pd.Timestamp(date)] = (
                            self.revenue[j], self.ref_revenue[i])

        ref_years = [pd.Timestamp(date).year for date in self.ref_dates]

        self.inconsistent_revenue = None
        old_revenue = None
        for i, revenue in enumerate(self.revenue):
            if pd.Timestamp(self.dates[i]).year in ref_years:
                pass
            elif old_revenue is not None and not (0.6 < revenue/old_revenue < 1.8):
                message = f'{self.ticker} has inconsistent revenue data\n'
                for i in range(len(self.dates)):
                    message += f'{self.dates[i]}: {self.revenue[i]}\n'
                self.inconsistent_revenue = message
                return False
            old_revenue = revenue

        return len(self.wrong_data) == 0
