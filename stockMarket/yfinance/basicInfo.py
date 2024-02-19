import yfinance as yf
import pandas as pd
import numpy as np
import os

from tqdm import tqdm

from stockMarket import __data_path__
from stockMarket.core import Contracts, ContractListType
from stockMarket.utils import Period

from ._common import tickers_to_change_name
from ._common import is_csv_file_up_to_date
from ._common import check_contracts_in_df
from ._common import write_to_csv


class BasicInfo:
    data_file = __data_path__.joinpath("basic_info.csv")
    empty_df = pd.DataFrame(columns=["Long Name", "Sector", "Price", "Trailing PE",
                            "Forward PE", "Market Cap", "Dividend Yield", "Payout Ratio"])

    def __init__(self, contracts: ContractListType):
        self.contracts = Contracts(contracts)

    def get_contract_infos(self, update: str | Period = "monthly") -> Contracts:
        self.df = self.empty_df
        self.to_update = not is_csv_file_up_to_date(
            self.data_file, update_period=update)
        self._init_df()
        check_contracts_in_df(self.contracts, self.df, self.to_update)

        if self.to_update:
            for contract in tqdm(self.contracts, desc="Basic Info"):

                self.long_name = ""
                self.sector = ""
                self.price = np.nan
                self.trailing_pe = np.nan
                self.forward_pe = np.nan
                self.market_cap = np.nan
                self.dividend_yield = np.nan
                self.payout_ratio = np.nan

                ticker = contract.ticker
                is_ticker_in_df = contract.ticker in self.df.index

                self._parse_df(ticker)
                self._get_data_from_yf(ticker)

                self._populate_df(is_ticker_in_df, ticker)

        self._populate_contracts()

        write_to_csv(self.df, self.data_file)

        return self.contracts

    def _init_df(self):
        if os.path.exists(self.data_file):
            self.df = pd.read_csv(self.data_file, index_col=0, header=1)

    def _parse_df(self, ticker: str) -> bool:
        self.long_name = self.df.loc[ticker, "Long Name"]

        if not isinstance(self.long_name, float):
            to_be_updated = False
        else:
            to_be_updated = True

        self.sector = self.df.loc[ticker, "Sector"]
        self.price = float(self.df.loc[ticker, "Price"])
        self.market_cap = float(self.df.loc[ticker, "Market Cap"])
        self.trailing_pe = float(self.df.loc[ticker, "Trailing PE"])
        self.forward_pe = float(self.df.loc[ticker, "Forward PE"])
        self.dividend_yield = float(self.df.loc[ticker, "Dividend Yield"])
        self.payout_ratio = float(self.df.loc[ticker, "Payout Ratio"])

        return to_be_updated

    def _get_data_from_yf(self, ticker):
        yf_ticker = ticker
        if yf_ticker in tickers_to_change_name:
            yf_ticker = tickers_to_change_name[ticker]

        yf_ticker = yf.Ticker(yf_ticker)
        info = yf_ticker.info
        self.long_name = info["longName"]
        self.sector = info["sector"]
        self.price = info["open"]

        if "marketCap" in info:
            self.market_cap = info["marketCap"] / 10**6

        if "trailingPE" in info:
            self.trailing_pe = info["trailingPE"]

        if "forwardPE" in info:
            self.forward_pe = info["forwardPE"]

        if "dividendYield" in info:
            self.dividend_yield = info["dividendYield"] * 100

        if "payoutRatio" in info:
            self.payout_ratio = info["payoutRatio"] * 100

    def _populate_df(self, is_ticker_in_df: bool, ticker: str):
        if not is_ticker_in_df:
            df_dict = {
                "Long Name": [self.long_name],
                "Sector": [self.sector],
                "Price": [self.price],
                "Trailing PE": [self.trailing_pe],
                "Forward PE": [self.forward_pe],
                "Market Cap": [self.market_cap],
                "Dividend Yield": [self.dividend_yield],
                "Payout Ratio": [self.payout_ratio]
            }

            self.df = pd.concat(
                [self.df, pd.DataFrame(df_dict, index=[ticker])])
        else:
            self.df.loc[ticker, "Long Name"] = self.long_name
            self.df.loc[ticker, "Sector"] = self.sector
            self.df.loc[ticker, "Price"] = self.price
            self.df.loc[ticker, "Trailing PE"] = self.trailing_pe
            self.df.loc[ticker, "Forward PE"] = self.forward_pe
            self.df.loc[ticker, "Market Cap"] = self.market_cap
            self.df.loc[ticker, "Dividend Yield"] = self.dividend_yield
            self.df.loc[ticker, "Payout Ratio"] = self.payout_ratio

    def _populate_contracts(self):
        for contract in self.contracts:
            if contract.ticker in self.df.index:
                contract.long_name = self.df.loc[contract.ticker, "Long Name"]
                contract.sector = self.df.loc[contract.ticker, "Sector"]
                contract.price = self.df.loc[contract.ticker, "Price"]
                contract.trailing_pe = self.df.loc[contract.ticker,
                                                   "Trailing PE"]
                contract.forward_pe = self.df.loc[contract.ticker,
                                                  "Forward PE"]
                contract.market_cap = self.df.loc[contract.ticker,
                                                  "Market Cap"]
                contract.dividend_yield = self.df.loc[contract.ticker,
                                                      "Dividend Yield"]
                contract.payout_ratio = self.df.loc[contract.ticker,
                                                    "Payout Ratio"]
