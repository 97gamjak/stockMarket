import yfinance as yf
import pandas as pd
import numpy as np
import datetime as dt
import os
from tqdm import tqdm

from beartype.typing import List

from stockMarket.core import Contract
from stockMarket import __data_path__


def to_date(x):
    return x.date()


vectorize_to_date = np.vectorize(to_date)


class Calendar:
    empty_df = pd.DataFrame(columns=["Earnings Dates"])
    data_file = __data_path__.joinpath("earnings_dates.csv")

    def __init__(self, contracts: List[str] | str | Contract | List[Contract]):
        contracts = np.atleast_1d(contracts)

        if isinstance(contracts[0], str):
            self.contracts = np.array(
                [Contract(ticker=contract) for contract in contracts])

        else:
            self.contracts = contracts

    def get_earnings_dates(self):

        if os.path.exists(self.data_file):
            self.calendar_df = pd.read_csv(self.data_file, index_col=0, converters={
                                           "Earnings Dates": list_date_converter})
        else:
            self.calendar_df = self.empty_df

        today = dt.datetime.today().date()

        for contract in tqdm(self.contracts, desc="Earnings Dates"):
            if contract.ticker in self.calendar_df.index:
                earnings_dates = self.calendar_df.loc[contract.ticker,
                                                      "Earnings Dates"]
                earnings_dates = earnings_dates[earnings_dates > today]
                if len(earnings_dates) > 0:
                    contract.earning_dates = earnings_dates
                    self.calendar_df.loc[contract.ticker,
                                         "Earnings Dates"] = earnings_dates
                    continue

            ticker = yf.Ticker(contract.ticker)

            try:
                earnings_dates = ticker.get_earnings_dates()
                earnings_dates = vectorize_to_date(
                    earnings_dates["EPS Estimate"].index)
                earnings_dates = np.unique(
                    earnings_dates[earnings_dates > today])
            except Exception:
                earnings_dates = []

            if contract.ticker in self.calendar_df.index:
                self.calendar_df.loc[contract.ticker,
                                     "Earnings Dates"] = earnings_dates
            else:
                self.calendar_df = pd.concat(
                    [self.calendar_df, pd.DataFrame({"Earnings Dates": [earnings_dates]}, index=[contract.ticker])])

            contract.earning_dates = earnings_dates

        self.calendar_df.to_csv(self.data_file)


def list_date_converter(x):
    x = x[1:-1]
    x = x.replace(", ", "-")
    x = x.replace("(", "")
    x = x.replace(")", "")
    list_x = x.split("datetime.date")
    list_x = [x.strip() for x in list_x if x.strip() != ""]
    list_x = [dt.datetime.strptime(x, "%Y-%m-%d").date() for x in list_x]
    return np.array(list_x)
