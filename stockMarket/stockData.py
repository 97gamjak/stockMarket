import yfinance as yf
import pandas as pd

from tqdm import tqdm


class StockData:
    def __init__(self, index, tickers=None):

        self.index = index
        self.companies = []
        self.tickers = tickers

        if index.lower().replace(" ", "") == 's&p500':
            self.companies = list(pd.read_html(
                'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol'])
        elif index.lower().replace(" ", "") == 'russell2000':

            df = tabula.read_pdf(
                "ru2000_membershiplist_20210628.pdf", pages="all")

            self.companies += [
                symbol for df_i in df for symbol in list(df_i['Ticker'])]
            self.companies += [
                symbol for df_i in df for symbol in list(df_i['Unnamed: 0'])]

            self.companies = [
                company for company in self.companies if isinstance(company, str)]
        else:
            raise ValueError("Index not supported")

    def init_data(self):
        self.tickers = self.download_tickers()

        self.tickers = {ticker: self.tickers[ticker]
                        for ticker in self.tickers if self.tickers[ticker] is not None}

        print("Retrieve info data from Yahoo Finance...")
        self.info = {
            ticker: self.tickers[ticker].info for ticker in tqdm(self.tickers)}

        print("Retrieve cashflow data from Yahoo Finance...")
        self.cashflow = {
            ticker: self.tickers[ticker].cashflow for ticker in tqdm(self.tickers)}

        print("Retrieve financials data from Yahoo Finance...")
        self.financials = {
            ticker: self.tickers[ticker].financials for ticker in tqdm(self.tickers)}

        print("Retrieve balancesheet data from Yahoo Finance...")
        self.balancesheet = {
            ticker: self.tickers[ticker].balancesheet for ticker in tqdm(self.tickers)}

        print("Retrieve calendar data from Yahoo Finance...")
        for ticker in tqdm(self.tickers):
            try:
                self.tickers[ticker].calendar
            except:
                self.tickers[ticker] = None

    def download_tickers(self):
        tickers = {}
        print()
        print("Downloading tickers...")
        print()
        for company in tqdm(self.companies):

            tickers[company] = yf.Ticker(company)

        return tickers
