import yfinance as yf
import pandas as pd
import tabula

from tqdm import tqdm

tickers_to_change_name = {
    "AVID": "CDMO",
    "BOMN": "BOC",
}

tickers_to_ignore = [
    "ONEM",  # bought by amazon
    "AERI",  # bought by Alcon
    "AJRD",  # bought by L3Harris
    "ANAT",  # bought by Core Specialty
    "ANGN",  # bought by Elicio Therapeutics
    "ATRS",  # bought by Halozyme Therapeutics
    "AAWW",  # bought by investor group
    "BPFH",  # bought by SVB Financial Group
    "EPAY",  # bought by Thoma Bravo
    "BRMK",  # bought by Ready Capital
    "BTX",   # bought by Resideo

    "ACBI",  # merged with South State
    "BXS",   # merged with Cadence Bancorporation
    "BCEI",  # merged with Extraction Oil & Gas
    "MNRL",  # merged with Sitio Royalties
    "ATCX",  # went private

    "NMTR",  # bankrupt
    "AMRS",  # bankrupt
    "ATNX",  # bankrupt
    "ATHX",  # bankrupt
    "AUD",   # bankrupt
    "AVYA",  # bankrupt

    "AGLE",  # not aviailable, penny stock

    # "AFIN",  # no idea why not available - some REIT
    # "HOME",  # no idea why not available
    # "BCOR",  # no idea why not available
    # "BVH",   # no idea why not available
]


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

        self.companies = [
            company for company in self.companies if company not in tickers_to_ignore]

        self.companies = [tickers_to_change_name[company]
                          if company in tickers_to_change_name else company for company in self.companies]

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
