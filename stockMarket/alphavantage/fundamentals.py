import glob

from tqdm import tqdm
from alpha_vantage.fundamentaldata import FundamentalData

from stockMarket import __data_path__


class Fundamentals:
    data_path = __data_path__ / 'alphavantage'

    def __init__(self, api_key, tickers):
        self.api_key = api_key
        self.tickers = tickers
        self.df = FundamentalData(key=self.api_key)

    def get_fundamentals_annual(self):

        for ticker in tqdm(self.tickers):
            try:
                if not (self.data_path / f'{ticker}_income_annual.csv').exists():
                    data = self.df.get_income_statement_annual(symbol=ticker)
                    data[0].to_csv(
                        self.data_path / f'{ticker}_income_annual.csv', sep="\t", index=False)

                if not (self.data_path / f'{ticker}_balance_annual.csv').exists():
                    data = self.df.get_balance_sheet_annual(symbol=ticker)
                    data[0].to_csv(
                        self.data_path / f'{ticker}_balance_annual.csv', sep="\t", index=False)

                if not (self.data_path / f'{ticker}_cashflow_annual.csv').exists():
                    data = self.df.get_cash_flow_annual(symbol=ticker)
                    data[0].to_csv(
                        self.data_path / f'{ticker}_cashflow_annual.csv', sep="\t", index=False)
            except Exception as e:
                print(f"Error for {ticker}: {e}")
                break

        list_of_files = glob.glob(str(self.data_path / '*.csv'))

        print(f"{len(list_of_files)/(len(self.tickers)*3)} files downloaded")
