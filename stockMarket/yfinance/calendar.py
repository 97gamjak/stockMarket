import yfinance as yf
import pandas as pd
import datetime as dt
import os

from tqdm import tqdm

from stockMarket.utils import Period
from stockMarket.core import Contracts, ContractListType
from stockMarket import __data_path__

from ._common import tickers_to_change_name
from ._common import is_csv_file_up_to_date
from ._common import check_contracts_in_df
from ._common import write_to_csv


class Calendar:
    earnings_date_key = "Earnings Dates"
    ex_dividend_date_key = "Ex-Dividend Dates"
    pays_dividend_key = "Pays Dividend"
    empty_df = pd.DataFrame(
        columns=[earnings_date_key, ex_dividend_date_key, pays_dividend_key])
    data_file = __data_path__.joinpath("calendar.csv")

    def __init__(self, contracts: ContractListType):
        self.contracts = Contracts(contracts)

    def get_calendar_events(self, update: str | Period = "monthly") -> Contracts:

        self.df = self.empty_df
        self.to_update = not is_csv_file_up_to_date(
            self.data_file, update_period=update)
        self._init_df()
        self._remove_old_dates()
        check_contracts_in_df(self.contracts, self.df, self.to_update)

        if self.to_update:
            for contract in tqdm(self.contracts, desc="Calendar Events"):

                self.earnings_date = pd.NaT
                self.ex_dividend_date = pd.NaT
                self.pays_dividend = True

                to_be_updated = True

                ticker = contract.ticker
                is_ticker_in_df = ticker in self.df.index

                if is_ticker_in_df:
                    to_be_updated = self._parse_df(ticker)

                if to_be_updated:
                    self._get_data_from_yf(ticker)

                self._populate_df(is_ticker_in_df, ticker)

        self._populate_contracts()

        write_to_csv(self.df, self.data_file)

        return self.contracts

    def _init_df(self):
        if os.path.exists(self.data_file):
            self.df = pd.read_csv(self.data_file, index_col=0, header=1)

            self.df[self.earnings_date_key] = pd.to_datetime(
                self.df[self.earnings_date_key]).dt.date
            self.df[self.ex_dividend_date_key] = pd.to_datetime(
                self.df[self.ex_dividend_date_key]).dt.date

    def _remove_old_dates(self):
        today = dt.datetime.today().date()

        for ticker in self.df.index:
            earnings_date = self.df.loc[ticker, self.earnings_date_key]
            ex_dividend_date = self.df.loc[ticker,
                                           self.ex_dividend_date_key]
            if earnings_date is pd.NaT or earnings_date < today:
                self.df.loc[ticker, self.earnings_date_key] = pd.NaT
            if ex_dividend_date is pd.NaT or ex_dividend_date < today:
                self.df.loc[ticker, self.ex_dividend_date_key] = pd.NaT

    def _parse_df(self, ticker: str) -> bool:
        to_be_updated = True

        earnings_date = self.df.loc[ticker, self.earnings_date_key]
        if earnings_date is not pd.NaT:
            to_be_updated = False

        ex_dividend_date = self.df.loc[ticker, self.ex_dividend_date_key]
        pays_dividend = self.df.loc[ticker, self.pays_dividend_key]

        if ex_dividend_date is not pd.NaT or not pays_dividend:
            to_be_updated = False

        return to_be_updated

    def _get_data_from_yf(self, ticker):
        yf_ticker = ticker
        if yf_ticker in tickers_to_change_name:
            yf_ticker = tickers_to_change_name[ticker]

        today = dt.datetime.today().date()

        yf_ticker = yf.Ticker(yf_ticker)
        calendar = yf_ticker.calendar

        if "Earnings Date" in calendar.keys():
            if len(calendar["Earnings Date"]) > 0:
                self.earnings_date = calendar["Earnings Date"][0]
                self.earnings_date = self.earnings_date if self.earnings_date > today else pd.NaT

        if "Ex-Dividend Date" in yf_ticker.calendar.keys():
            self.ex_dividend_date = yf_ticker.calendar["Ex-Dividend Date"]
            self.ex_dividend_date = self.ex_dividend_date if self.ex_dividend_date > today else pd.NaT
            self.pays_dividend = True

    def _populate_df(self, is_ticker_in_df: bool, ticker: str):
        if is_ticker_in_df:
            self.df.loc[ticker, self.earnings_date_key] = self.earnings_date
            self.df.loc[ticker, self.pays_dividend_key] = self.pays_dividend
            self.df.loc[ticker,
                        self.ex_dividend_date_key] = self.ex_dividend_date
        else:
            df_dict = {
                self.earnings_date_key: [self.earnings_date],
                self.pays_dividend_key: [self.pays_dividend],
                self.ex_dividend_date_key: [self.ex_dividend_date]
            }
            self.df = pd.concat(
                [self.df, pd.DataFrame(df_dict, index=[ticker])])

        self.df[self.pays_dividend_key] = self.df[self.pays_dividend_key].astype(
            bool)

    def _populate_contracts(self):
        for contract in self.contracts:
            if contract.ticker in self.df.index:
                contract.earnings_date = self.df.loc[contract.ticker,
                                                     self.earnings_date_key]
                contract.ex_dividend_date = self.df.loc[contract.ticker,
                                                        self.ex_dividend_date_key]
                contract.pays_dividend = self.df.loc[contract.ticker,
                                                     self.pays_dividend_key]
