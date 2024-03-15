import datetime as dt
import numpy as np
import pandas as pd
import re
import glob
import shutil

from pathlib import Path
from beartype.typing import List
from tqdm import tqdm
from openpyxl import load_workbook

from .technicals import Technicals
from .strategyObjects import StrategyObject, RuleEnum
from stockMarket.utils import Period


class Strategy:
    storing_behavior_flags = (
        "full_overwrite", "matching_overwrite", "append", "abort", "numerical")

    def __init__(self,
                 strategy_objects: List[StrategyObject],
                 start_date: str,
                 end_date: str,
                 rule_enums: List[RuleEnum] = [RuleEnum.BULLISH],
                 candle_period: str | Period | None = None,
                 base_path: str = "strategy_testing",
                 storing_behavior: str | None = "numerical",
                 ) -> None:

        self.setup_dates(start_date, end_date, candle_period)

        self.storing_behavior = storing_behavior.lower()
        self.base_path = Path(base_path)

        self.compile_strategy(strategy_objects, rule_enums)

        self.result_logger_filename = str(self.dir_path / "result_logger.txt")
        self.error_logger_filename = str(self.dir_path / "error_logger.txt")

        self.result_logger = {}
        self.meta_data_logger = {}
        self.error_logger = {}

    def compile_strategy(self,
                         strategy_objects: List[StrategyObject],
                         rule_enums: List[RuleEnum]
                         ) -> None:
        self.strategy_objects = strategy_objects
        self.rule_enums = rule_enums

        strategy_names = [
            strategy_object.strategy_name for strategy_object in self.strategy_objects]
        self.dir_name = "_".join([name for name in sorted(strategy_names)])

        if self.storing_behavior not in self.storing_behavior_flags:
            raise NotImplementedError(
                f"Storing behavior not implemented, possible values are: {self.storing_behavior_flags}")

        if not self.base_path.exists():
            self.base_path.mkdir()

        self.dir_path = self.base_path / self.dir_name

        if self.storing_behavior == "numerical":

            if self.dir_path.exists():
                reserved_dir_names = glob.glob(
                    str(self.dir_path) + "_*")
                dir_numbers = sorted([int(name.split("_")[-1])
                                      for name in reserved_dir_names])
                if dir_numbers == []:
                    self.dir_path = Path(str(self.dir_path) + "_1")
                else:
                    self.dir_path = Path(
                        str(self.dir_path) + f"_{dir_numbers[-1] + 1}")

        elif self.storing_behavior == "abort":

            if self.dir_path.exists():
                raise FileExistsError(
                    f"Directory {self.dir_path} already exists, aborting")

        elif self.storing_behavior == "full_overwrite":
            print(self.dir_path)
            if self.dir_path.exists():
                print(self.dir_path)
                shutil.rmtree(self.dir_path)

            if self.dir_path.exists():
                print(self.dir_path)

        self.dir_path.mkdir()

    def setup_dates(self, start_date, end_date, candle_period):
        if candle_period is None:
            self.candle_period = Period('daily')
        else:
            self.candle_period = Period(candle_period)

        today = dt.datetime.now().date()
        self.start_date, self.end_date = _check_dates(start_date, end_date)

        period_time = (today - self.start_date).days + 1
        self.n_bars = np.ceil(
            period_time / self.candle_period.period_time.days)
        self.n_bars = int(self.n_bars) + 100

    # def read_xlsx(self, file_path: str) -> pd.DataFrame:

    def screen(self, tickers: List[str] | str) -> None:

        self.tickers = sorted(np.atleast_1d(tickers))

        logger_file = open(self.result_logger_filename, "w")
        error_file = open(self.error_logger_filename, "w")
        meta_file = open(str(self.dir_path / "meta_data_logger.txt"), "w")

        #fmt: off
        logger_file.write(f"Screening for {self.candle_period.period_string} candles from {self.start_date} to {self.end_date}\n\n\n")
        #fmt: on

        xlsx_file = load_workbook(filename=str(
            self.base_path / "template.xlsx"))

        xlsx_sheet = xlsx_file["screening"]

        for ticker in tqdm(self.tickers):
            contract = Technicals(ticker=ticker)

            prices_retrieved = False
            try_outs = 0
            while not prices_retrieved and try_outs < 5:
                try:
                    try_outs += 1
                    contract.init_pricing_data(
                        self.candle_period, n_bars=self.n_bars)
                    prices_retrieved = True
                except Exception as e:
                    prices_retrieved = False

            if not prices_retrieved:
                self.error_logger[ticker] = "Pricing data not retrieved"
                error_file.write(f"Ticker: {ticker}\n")
                error_file.write(f"{self.error_logger[ticker]}\n")
                error_file.write("\n")
                error_file.flush()

                continue

            pricing_data = contract.pricing_data
            self.result_logger[ticker] = {}
            self.meta_data_logger[ticker] = {}

            try:
                for strategy_object in self.strategy_objects:
                    strategy_object.data = pricing_data
                    strategy_object.calculate_indicators()
            except Exception as e:
                self.error_logger[ticker] = e
                error_file.write(f"Ticker: {ticker}\n")
                error_file.write(f"{self.error_logger[ticker]}\n")
                error_file.write("\n")
                error_file.flush()

                continue

            end_index = _calculate_end_date_index(
                pricing_data, self.end_date)

            for index in -np.arange(end_index, len(pricing_data) + 1):
                date = get_date_from_pricing_data(pricing_data, index)

                if pd.Timestamp(self.start_date).date() > date:
                    break

                date = pricing_data.iloc[index].name
                for rule_enum in self.rule_enums:
                    combined_rule_outcome = True

                    for strategy_object in self.strategy_objects:
                        rule_outcome = strategy_object.evaluate_rules(
                            index, self.rule_enums)
                        combined_rule_outcome &= rule_outcome[rule_enum.value]

                    if combined_rule_outcome:
                        self.result_logger[ticker][date] = (
                            rule_enum.value, pricing_data.iloc[index])
                        for strategy_object in self.strategy_objects:
                            if hasattr(strategy_object, "meta_data"):
                                self.meta_data_logger[ticker][date] = strategy_object.meta_data[index]

            if self.result_logger[ticker] != {}:

                logger_file.write(f"Ticker: {ticker}\n")
                for key, value in self.result_logger[ticker].items():
                    logger_file.write(f"{key}: {value[0]}\n")
                logger_file.write("\n")
                logger_file.flush()

                meta_file.write(f"Ticker: {ticker}\n")
                for key, value in self.meta_data_logger[ticker].items():
                    meta_file.write(f"{key}\n")
                    meta_file.write(value)
                meta_file.write("\n")
                meta_file.flush()

        row = 2
        for i, ticker in enumerate(self.tickers):
            for key, value in self.result_logger[ticker].items():
                date = key.date()
                candle = value[1]
                rule_type = value[0]
                xlsx_sheet.cell(row=row, column=1).value = date
                xlsx_sheet.cell(row=row, column=2).value = ticker
                xlsx_sheet.cell(row=row, column=5).value = candle.close
                xlsx_sheet.cell(row=row, column=6).value = candle.low
                row += 1

        logger_file.close()
        meta_file.close()
        xlsx_file.save(str(self.dir_path / "screening.xlsx"))


def _check_dates(start_date: str, end_date: str) -> tuple[dt.date, dt.date]:
    pattern = re.compile(r"\d{2}.\d{2}.\d{4}")
    if not pattern.fullmatch(start_date):
        raise ValueError("Start date is not in the correct format")
    if not pattern.fullmatch(end_date):
        raise ValueError("End date is not in the correct format")

    start_date = dt.datetime.strptime(start_date, "%d.%m.%Y").date()
    end_date = dt.datetime.strptime(end_date, "%d.%m.%Y").date()

    if end_date <= start_date:
        raise ValueError("End date is before or equal start date")

    return start_date, end_date


def _calculate_end_date_index(pricing_data, end_date):
    index = -1
    end_date = pd.Timestamp(end_date).date()
    while -index < len(pricing_data):
        date = get_date_from_pricing_data(pricing_data, index)

        if date < end_date:
            break

        index -= 1

    return abs(index)


def get_date_from_pricing_data(pricing_data, index):
    return pricing_data.index[index].date()
