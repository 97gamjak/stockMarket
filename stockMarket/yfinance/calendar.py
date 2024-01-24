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
    empty_df = pd.DataFrame(
        columns=["Earnings Dates", "Pays Dividend", "Ex-Dividend Dates"])
    data_file = __data_path__.joinpath("calendar.csv")

    def __init__(self, contracts: List[str] | str | Contract | List[Contract]):
        contracts = np.atleast_1d(contracts)

        if isinstance(contracts[0], str):
            self.contracts = np.array(
                [Contract(ticker=contract) for contract in contracts])

        else:
            self.contracts = contracts

    def get_calendar_events(self):

        if os.path.exists(self.data_file):
            print(self.data_file)
            self.calendar_df = pd.read_csv(
                self.data_file, index_col=0)
        else:
            self.calendar_df = self.empty_df

        today = dt.datetime.today().date()

        for contract in tqdm(self.contracts, desc="Calendar Events"):
            print(contract.ticker)
            to_be_updated = True
            earnings_date = None
            ex_dividend_date = None
            pays_dividend = True

            if contract.ticker in self.calendar_df.index:
                #############################
                to_be_updated = False
                print(contract.ticker)
                print(self.calendar_df.index)
                earnings_date = self.calendar_df.loc[contract.ticker,
                                                     "Earnings Dates"]
                earnings_date = pd.Timestamp.fromisoformat(
                    earnings_date).date() if isinstance(earnings_date, str) else None
                if earnings_date is None or earnings_date > today:
                    to_be_updated = True

                pays_dividend = self.calendar_df.loc[contract.ticker,
                                                     "Pays Dividend"]
                if pays_dividend:
                    ex_dividend_date = self.calendar_df.loc[contract.ticker,
                                                            "Ex-Dividend Dates"]
                    ex_dividend_date = pd.Timestamp.fromisoformat(
                        ex_dividend_date).date() if isinstance(ex_dividend_date, str) else None
                    if ex_dividend_date is None or ex_dividend_date > today:
                        to_be_updated = True

            if to_be_updated:

                ticker = yf.Ticker(contract.ticker)

                try:
                    earnings_date = ticker.calendar["Earnings Date"][0]
                    if earnings_date < today:
                        earnings_date = None

                    if "Ex-Dividend Date" in ticker.calendar.keys():
                        ex_dividend_date = ticker.calendar["Ex-Dividend Date"]
                        ex_dividend_date = ex_dividend_date if ex_dividend_date > today else None
                        pays_dividend = True
                    else:
                        ex_dividend_date = None
                        pays_dividend = False

                except Exception:
                    earnings_date = None
                    ex_dividend_date = None
                    pays_dividend = False

            if contract.ticker in self.calendar_df.index:
                self.calendar_df.loc[contract.ticker,
                                     "Earnings Dates"] = earnings_date
            else:
                self.calendar_df = pd.concat(
                    [self.calendar_df, pd.DataFrame({"Earnings Dates": [earnings_date]}, index=[contract.ticker])])

            self.calendar_df.loc[contract.ticker,
                                 "Pays Dividend"] = pays_dividend
            self.calendar_df.loc[contract.ticker,
                                 "Ex-Dividend Dates"] = ex_dividend_date

            contract.earning_date = earnings_date
            contract.ex_dividend_date = ex_dividend_date

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
