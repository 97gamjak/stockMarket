import yfinance as yf
import pandas as pd
import numpy as np
import datetime as dt
import os
from tqdm import tqdm

from beartype.typing import List

from stockMarket.core import Contract
from stockMarket import __data_path__


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

    def get_calendar_events(self, include_dividends=True):

        if os.path.exists(self.data_file):
            print(self.data_file)
            self.calendar_df = pd.read_csv(
                self.data_file, index_col=0)
        else:
            self.calendar_df = self.empty_df

        today = dt.datetime.today().date()

        for contract in tqdm(self.contracts, desc="Calendar Events"):
            to_be_updated = True
            earnings_date = None
            ex_dividend_date = None
            pays_dividend = True

            is_ticker_in_df = contract.ticker in self.calendar_df.index

            if is_ticker_in_df:

                earnings_date, to_be_updated = self._get_earnings_from_df(
                    contract.ticker, today, to_be_updated=False)

                ex_dividend_date, pays_dividend, to_be_updated = self._get_dividends_from_df(
                    contract.ticker, today, to_be_updated, include_dividends)

            if to_be_updated:

                yf_ticker = yf.Ticker(contract.ticker)

                earnings_date = _get_earnings_date_from_yf(yf_ticker, today)

                if include_dividends:
                    ex_dividend_date, pays_dividend = _get_dividends_from_yf(
                        yf_ticker, today)

            if is_ticker_in_df:
                self.calendar_df.loc[contract.ticker,
                                     "Earnings Dates"] = earnings_date
            else:
                self.calendar_df = pd.concat(
                    [self.calendar_df, pd.DataFrame({"Earnings Dates": [earnings_date]}, index=[contract.ticker])])

            self.calendar_df.loc[contract.ticker,
                                 "Pays Dividend"] = pays_dividend
            self.calendar_df.loc[contract.ticker,
                                 "Ex-Dividend Dates"] = ex_dividend_date

            contract.earnings_date = earnings_date
            contract.ex_dividend_date = ex_dividend_date
            contract.pays_dividend = pays_dividend

        self.calendar_df.to_csv(self.data_file)

    def _get_earnings_from_df(self, ticker, today: dt.date, to_be_updated: bool):
        earnings_date = self.calendar_df.loc[ticker, "Earnings Dates"]
        earnings_date = pd.Timestamp.fromisoformat(
            earnings_date).date() if isinstance(earnings_date, str) else None

        if earnings_date is None or earnings_date < today:
            to_be_updated = True

        return earnings_date, to_be_updated

    def _get_dividends_from_df(self, ticker, today: dt.date, to_be_updated: bool, include_dividends: bool):
        ex_dividend_date = None
        pays_dividend = self.calendar_df.loc[ticker, "Pays Dividend"]
        if pays_dividend and include_dividends:
            ex_dividend_date = self.calendar_df.loc[ticker,
                                                    "Ex-Dividend Dates"]
            ex_dividend_date = pd.Timestamp.fromisoformat(
                ex_dividend_date).date() if isinstance(ex_dividend_date, str) else None
            if ex_dividend_date is None or ex_dividend_date < today:
                to_be_updated = True

        return ex_dividend_date, pays_dividend, to_be_updated


def _get_earnings_date_from_yf(yf_ticker, today: dt.date):
    try:
        earnings_date = yf_ticker.calendar["Earnings Date"][0]
        earnings_date = earnings_date if earnings_date > today else None
    except Exception:
        earnings_date = None

    return earnings_date


def _get_dividends_from_yf(yf_ticker, today: dt.date):
    try:
        if "Ex-Dividend Date" in yf_ticker.calendar.keys():
            ex_dividend_date = yf_ticker.calendar["Ex-Dividend Date"]
            ex_dividend_date = ex_dividend_date if ex_dividend_date > today else None
            pays_dividend = True
        else:
            ex_dividend_date = None
            pays_dividend = False
    except Exception:
        ex_dividend_date = None
        pays_dividend = False

    return ex_dividend_date, pays_dividend
