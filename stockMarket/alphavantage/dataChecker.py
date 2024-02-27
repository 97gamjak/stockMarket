import pandas as pd

from stockMarket.core import Contract
from stockMarket import __data_path__


class DataChecker:
    data_path = __data_path__ / 'alphavantage'

    def __init__(self, contract: Contract):
        self.ticker = contract.ticker
        self.income = self.parse_alphavantage_df(file)
        self.balance = self.parse_alphavantage_df(file)
        self.cashflow = self.parse_alphavantage_df(file)

    def check_data(self):
        self.fiscal_year_ends = contract.fiscal_year_end_dates
        self.fiscal_year_ends = [pd.Timestamp(
            date) for date in self.fiscal_year_ends]

        for date in self.fiscal_year_ends:
            income_data = self.income.loc[date]
            self.check_data_income(data)

    def check_data_income(self, data):
        data

    def parse_alphavantage_df(self, file):
        return pd.read_csv(file, sep="\t", index_col="fiscalDateEnding", parse_dates=True)
