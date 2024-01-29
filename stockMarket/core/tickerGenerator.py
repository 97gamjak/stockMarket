import numpy as np
import pandas as pd

from beartype.typing import List

from stockMarket import __data_path__


def get_tickers_from_index(index: str | List[str]) -> List[str]:
    return TickerGenerator(index).generate_tickers()


class TickerGenerator:
    russell_2000_file = __data_path__.joinpath("russell2000.csv")

    def __init__(self, indices=str | List[str]):
        self.indices = indices
        self.tickers = []

    def generate_tickers(self) -> List[str]:

        for index in np.atleast_1d(self.indices):
            index = index.lower().replace(" ", "")
            if index == 's&p500' or index == 'sp500':

                self.tickers += list(pd.read_html(
                    'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol'])

            elif index == 'russell2000':

                self.tickers += list(pd.read_csv(
                    self.russell_2000_file)["Ticker"].values)

            else:
                raise ValueError("Index not supported")

        return self.tickers
