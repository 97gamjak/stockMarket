import numpy as np
import datetime as dt
import requests
import warnings
import glob

from pathlib import Path
from sec_edgar_downloader import Downloader as _Downloader
from sec_cik_mapper import StockMapper
from beartype.typing import List, Optional
from tqdm import tqdm

from stockMarket import __data_path__
from stockMarket.config import headers


class Downloader:
    filings_path = __data_path__ / "sec-edgar-filings"

    def __init__(self, tickers: str | List[str]):
        self.tickers = np.atleast_1d(tickers)

    def download_10k_reports(self, include_amends=False, download_details=False, fast_download=False):
        if fast_download:
            tickers_to_download = []
            for ticker in self.tickers:
                ticker_path = self.filings_path / ticker / "10-K"
                if not ticker_path.exists():
                    tickers_to_download.append(ticker)
        else:
            tickers_to_download = self.tickers

        for ticker in tqdm(tickers_to_download):
            dl = _Downloader(
                "stockMarket", "97gamjak@gmail.com", __data_path__)
            dl.get("10-K", ticker, include_amends=include_amends,
                   download_details=download_details)

    def download_financial_statements_xlsx(self, from_year: Optional[int] = None):
        from_year = int(str(from_year)[-2:])
        max_year = int(str(dt.date.today().year)[-2:])
        mapper = StockMapper()

        for ticker in tqdm(self.tickers):
            cik = mapper.ticker_to_cik[ticker]

            ticker_path = self.filings_path / ticker / "10-K"

            if not ticker_path.exists():
                message = f"No 10-K reports found for {ticker} with cik {cik}"
                warnings.warn(message, UserWarning)
                continue

            for report in glob.glob(str(ticker_path / "*")):
                report = Path(report)
                if not report.is_dir() or (report / "Financial_Report.xlsx").exists():
                    continue

                year = int(report.name.split("-")[-2])

                if from_year and year < from_year and year > max_year:
                    continue

                report_number = str(report).split("/")[-1].replace("-", "")

                url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{report_number}/Financial_Report.xlsx"
                response = requests.get(url, headers=headers)

                if response.status_code != 200:
                    message = f"Failed to download {url} for {ticker}"
                    warnings.warn(message, UserWarning)

                with open(report / "Financial_Report.xlsx", "wb") as f:
                    f.write(response.content)
