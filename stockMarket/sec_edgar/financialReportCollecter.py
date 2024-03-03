import numpy as np
import datetime as dt
import pandas as pd
import warnings
import glob
from tqdm import tqdm

from beartype.typing import List, Optional

from stockMarket import __data_path__
from .financialReportReader import FinancialReportReader


class FinancialReportCollecter:
    sec_edgar_path = __data_path__ / 'sec-edgar-filings'

    def __init__(self, tickers: List[str] | str, max_errors: Optional[int] = 0):
        self.tickers = np.atleast_1d(tickers)
        self.max_errors = max_errors

        self.error_messages = []

    def collect(self, from_year: Optional[int] = None, update: bool = False):

        if from_year is not None:
            from_year = int(str(from_year)[2:])

        for ticker in tqdm(self.tickers):
            ticker_path = self.sec_edgar_path / ticker / '10-K'

            csv_file = ticker_path / 'full_income.csv'

            if csv_file.exists() and not update:
                continue

            csv_file = str(csv_file)

            if not ticker_path.exists():
                raise FileNotFoundError(
                    f'{ticker} is not found in the sec-edgar-filings directory')

            list_of_reports = glob.glob(
                str(ticker_path) + '/*/Financial_Report.xlsx')

            available_years = self.find_years_from_paths(
                list_of_reports, from_year, ticker)

            list_of_reports = [report for report in list_of_reports if int(report.split(
                '-')[-2]) in available_years]
            list_of_reports = sorted(
                list_of_reports, key=lambda x: int(x.split('-')[-2]))

            df = pd.DataFrame()

            for report_file in list_of_reports:
                try:
                    reader = FinancialReportReader(report_file)
                    date, data = reader.read_income()
                except Exception as e:
                    self.error_messages.append(
                        f'Error reading {report_file} for {ticker}: {e}')
                    if self.max_errors is not None and len(self.error_messages) > self.max_errors:
                        print(self.error_messages)
                        raise e

                    continue

                dictionary = {"endDate": date}
                for key, value in data.items():
                    dictionary[key] = value

                data_df = pd.DataFrame([dictionary])
                df = pd.concat([df, data_df])

            df.to_csv(csv_file, index=False)

    def find_years_from_paths(self, paths: List[str], from_year, ticker) -> List[int]:
        available_years = []
        for path in paths:
            year = int(path.split('-')[-2])
            available_years.append(year)

        year_today = int(str(dt.datetime.now().year)[2:])

        if from_year is None:
            available_years = [
                year for year in available_years if year <= year_today]
        else:
            available_years = [
                year for year in available_years if from_year <= year <= year_today]

        available_years.sort()

        if available_years != list(range(available_years[0], available_years[-1]+1)):
            warnings.warn(
                f'{ticker} does not have all reports for the years {available_years[0]} to {year_today}')

        if (from_year and available_years[0] != from_year) or available_years[-1] < year_today - 1:
            warnings.warn(
                f'{ticker} does only have reports from {available_years[0]} to {available_years[-1]}')

        return available_years
