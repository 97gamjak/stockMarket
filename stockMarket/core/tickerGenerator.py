import numpy as np
import pandas as pd
import requests

from tqdm import tqdm
from beartype.typing import List, Tuple

from stockMarket import __data_path__
from stockMarket.config import tickers_to_ignore, tickers_to_change_name


def get_tickers_from_index(index: str | List[str]) -> List[str]:
    return TickerGenerator(index).generate_tickers()


def get_ticker_from_isin(isin: str) -> str:
    url = 'https://query1.finance.yahoo.com/v1/finance/search'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.109 Safari/537.36',
    }

    params = dict(
        q=isin,
        quotesCount=1,
        newsCount=0,
        listCount=0,
        quotesQueryId='tss_match_phrase_query'
    )

    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    if "quotes" in data and len(data["quotes"]) > 0:
        ticker = data["quotes"][0]["symbol"]
    else:
        raise ValueError(f"ISIN {isin} not found")

    return ticker


def get_currencies_from_index(index: str | List[str]) -> List[Tuple[str, str]]:
    return TickerGenerator(index).generate_currencies()


class TickerGenerator:
    russell_2000_file = __data_path__.joinpath("russell2000.csv")
    euro_stoxx_600_file = __data_path__.joinpath("euro_stoxx600.csv")

    sp500_names = ['s&p500', 'sp500']
    russell_2000_names = ['russell2000']
    euro_stoxx_600_names = ['eurostoxx600', 'euro_stoxx600', "euro_stoxx_600"]
    nasdaq_100_names = ['nasdaq100', 'nasdaq_100', 'nasdaq']

    indices_names = sp500_names + russell_2000_names + \
        euro_stoxx_600_names + nasdaq_100_names

    def __init__(self, indices=str | List[str]):
        self.indices = np.atleast_1d(indices)
        if self.indices[0] == "all":
            self.indices = self.indices_names

        self.indices = [index.lower().replace(" ", "")
                        for index in self.indices]

        for index in self.indices:
            if index not in self.indices_names:
                raise ValueError("Index not supported")

    def generate_tickers(self) -> List[str]:

        tickers = []

        for index in self.indices:
            tickers += self.generate_tickers_single_index(index)

        return list(set(tickers))

    def generate_tickers_single_index(self, index: str) -> List[str]:
        if index in self.sp500_names:
            tickers = self.get_sp500_tickers()

        if index in self.russell_2000_names:
            tickers = list(pd.read_csv(self.russell_2000_file)
                           ["Ticker"].values)

        if index in self.euro_stoxx_600_names:
            tickers = self.get_euro_stoxx_600_tickers()

        if index in self.nasdaq_100_names:
            tickers = self.get_nasdaq_100_tickers()

        tickers_cleaned = []
        for ticker in tickers:
            if ticker in tickers_to_ignore:
                continue

            if ticker in tickers_to_change_name:
                ticker = tickers_to_change_name[ticker]

            tickers_cleaned.append(ticker)

        return list(set(tickers_cleaned))

    def get_russell_2000_tickers(self) -> List[str]:
        return list(pd.read_csv(self.russell_2000_file)["Ticker"].values)

    def get_sp500_tickers(self) -> List[str]:
        return list(pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol'])

    def get_nasdaq_100_tickers(self) -> List[str]:
        return list(pd.read_html('https://de.wikipedia.org/wiki/NASDAQ-100')[-1]['Symbol'])

    def get_euro_stoxx_600_tickers(self) -> List[str]:
        df = pd.read_csv(self.euro_stoxx_600_file)

        if "Ticker" not in df.columns:
            isins = df["ISIN"].values
            tickers = []

            for isin in tqdm(isins, desc="Getting Euro Stoxx 600 tickers from ISINs"):

                name = df.loc[df["ISIN"] ==
                              isin, "Name"].values[0]
                if isin.startswith("_"):
                    ticker = None
                elif name in names_to_ignore:
                    ticker = None
                else:
                    ticker = get_ticker_from_isin(isin)

                tickers.append(ticker)

            df["Ticker"] = tickers
            df.to_csv(self.euro_stoxx_600_file, index=False)

        tickers = df["Ticker"].values
        tickers = [
            ticker for ticker in tickers if not isinstance(ticker, float)]

        return tickers

    def generate_currencies(self) -> List[Tuple[str, str]]:
        ticker_currency_tuples = []

        # TODO:
        crude_hack = {"TUI": "TUI1.F"}

        for index in self.indices:
            tickers = self.generate_tickers_single_index(index)

            if index not in self.euro_stoxx_600_names:
                currencies = ["USD" for _ in tickers]

            else:
                pd.read_csv(self.euro_stoxx_600_file)
                df = pd.read_csv(self.euro_stoxx_600_file)

                currencies = []
                for ticker in tickers:
                    if ticker in crude_hack:
                        ticker = crude_hack[ticker]
                    currency = df.loc[df["Ticker"] ==
                                      ticker, "Currency"].values[0]

                    currencies.append(currency)

            for ticker, currency in zip(tickers, currencies):
                ticker_currency_tuples.append((ticker, currency))

        return list(set(ticker_currency_tuples))


names_to_ignore = [
    "KESKO ORD",
    "DEUTSCHE GLOBAL LIQUIDITY SERI",
    "NMC HEALTH PLC",
]
