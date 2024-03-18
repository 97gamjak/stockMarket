import datetime as dt
import numpy as np
import pandas as pd
import yfinance as yf
import re
import glob
import shutil
import os

from pathlib import Path
from beartype.typing import List, Optional
from tqdm import tqdm
from openpyxl import load_workbook
from finance_calendars import finance_calendars as fc

from .strategyObjects import StrategyObject, RuleEnum
from .trade.trade import Trade, TradeSettings
from stockMarket.utils import Period
from stockMarket.yfinance._common import adjust_price_data_from_df


class Strategy:
    storing_behavior_flags = (
        "full_overwrite", "matching_overwrite", "append", "abort", "numerical")

    def __init__(self,
                 strategy_objects: List[StrategyObject],
                 start_date: str,
                 end_date: str,
                 rule_enums: List[RuleEnum] = [RuleEnum.BULLISH],
                 trade_settings: Optional[TradeSettings] = None,
                 candle_period: str | Period | None = None,
                 base_path: str = "strategy_testing",
                 storing_behavior: str | None = "numerical",
                 template_xlsx_file: str = "template_new.xlsx",
                 xlsx_file: str = "screening.xlsx",
                 use_earnings_dates: bool = False,
                 finalize_commands=None,
                 ) -> None:

        self.setup_dates(start_date, end_date, candle_period)

        self.storing_behavior = storing_behavior.lower()
        self.base_path = Path(base_path)

        self.compile_strategy(strategy_objects, rule_enums)
        self.trade_settings = trade_settings

        self.result_logger_filename = str(self.dir_path / "result_logger.txt")
        self.error_logger_filename = str(self.dir_path / "error_logger.txt")
        self.template_xlsx_file = str(self.base_path / template_xlsx_file)
        self.xlsx_filename = str(self.dir_path / xlsx_file)

        self.trades = {}
        self.meta_data_logger = {}
        self.error_logger = {}

        self.use_earnings_dates = use_earnings_dates

        if finalize_commands is None:
            finalize_commands = []

        self.finalize_commands = np.atleast_1d(finalize_commands)

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
                reserved_dir_names = [
                    name for name in reserved_dir_names if name.split("_")[-1].isdigit()]
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
            if self.dir_path.exists():
                shutil.rmtree(self.dir_path)

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

    def get_earnings_dates(self):
        self.earnings_calendar = {ticker: [] for ticker in self.tickers}
        date = pd.Timestamp(self.start_date).date()
        end_date = pd.Timestamp(self.end_date).date()
        while date < end_date:
            earnings = fc.get_earnings_by_date(date)
            for ticker in self.tickers:
                if ticker in earnings.index:
                    self.earnings_calendar[ticker].append(date)

            date += pd.Timedelta(days=1)

    def find_next_earnings_date(self, ticker, date):
        date = pd.Timestamp(date).date()
        earnings_dates = self.earnings_calendar[ticker]
        for earnings_date in earnings_dates:
            if earnings_date > date:
                return earnings_date, (earnings_date - date).days
        return "No earnings date found", None

    def write_xlsx_file(self):
        xlsx_file = load_workbook(filename=self.template_xlsx_file)
        xlsx_sheet = xlsx_file["stocks"]
        row = 3

        for trades in self.trades.values():
            for trade in trades:
                xlsx_sheet.cell(row=row, column=1).value = trade.TC_date
                xlsx_sheet.cell(row=row, column=2).value = trade.ENTRY_date
                xlsx_sheet.cell(row=row, column=3).value = trade.ticker
                xlsx_sheet.cell(row=row, column=4).value = trade.ENTRY
                xlsx_sheet.cell(
                    row=row, column=5).value = trade.R_ENTRY
                xlsx_sheet.cell(row=row, column=6).value = trade.SL
                xlsx_sheet.cell(
                    row=row, column=7).value = trade.TP_date
                xlsx_sheet.cell(row=row, column=8).value = trade.TP
                xlsx_sheet.cell(row=row, column=9).value = trade.EXIT_date
                xlsx_sheet.cell(row=row, column=10).value = trade.EXIT

                if trade.trade_executed and trade.TC_date is None:
                    xlsx_sheet.cell(
                        row=row, column=11).value = "To Be Determined"
                elif trade.trade_executed and trade.EXIT_date is None:
                    xlsx_sheet.cell(row=row, column=11).value = "Open"
                elif trade.trade_executed and trade.EXIT_date is not None:
                    xlsx_sheet.cell(row=row, column=11).value = "Closed"
                else:
                    xlsx_sheet.cell(row=row, column=11).value = "Not Executed"

                if self.use_earnings_dates:
                    xlsx_sheet.cell(row=row, column=12).value = self.find_next_earnings_date(
                        trade.ticker, trade.candle_date)[1]

                row += 1

        xlsx_file.save(self.xlsx_filename)

    def screen(self, tickers: List[str] | str) -> None:

        self.tickers = sorted(np.atleast_1d(tickers))

        if self.use_earnings_dates:
            self.get_earnings_dates()

        logger_file = open(self.result_logger_filename, "w")
        meta_file = open(str(self.dir_path / "meta_data_logger.txt"), "w")

        #fmt: off
        logger_file.write(f"Screening for {self.candle_period.period_string} candles from {self.start_date} to {self.end_date}\n\n\n")
        #fmt: on

        for ticker in tqdm(self.tickers):
            pricing_data = self.populate_pricing_data(ticker)
            self._screen_single_ticker(ticker, pricing_data)

        self.write_xlsx_file()

        logger_file.close()
        meta_file.close()
        for command in self.finalize_commands:
            os.system(command)

    def populate_pricing_data(self, ticker: str) -> None:
        error_file = open(self.error_logger_filename, "w")

        ticker = yf.Ticker(ticker)
        start_date = pd.Timestamp(self.start_date).date()
        start_date -= pd.Timedelta(days=100 *
                                   self.candle_period.period_time.days)

        pricing_data = ticker.history(
            auto_adjust=False,
            start=str(start_date),
            end=None,
            rounding=True,
            interval=self.candle_period.yf_interval
        )

        pricing_data = adjust_price_data_from_df(pricing_data)

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

            return None

        return pricing_data

    def _screen_single_ticker(self, ticker: str, pricing_data) -> None:

        if pricing_data is None:
            return

        self.trades[ticker] = []
        self.meta_data_logger[ticker] = {}

        end_index = _calculate_end_date_index(
            pricing_data, self.end_date)

        for index in -np.arange(end_index, len(pricing_data) + 1):
            date = get_date_from_pricing_data(pricing_data, index)

            if pd.Timestamp(self.start_date).date() > date:
                break

            date = pricing_data.iloc[index].name

            rule_outcome = [strategy_object.evaluate_rules(
                index) for strategy_object in self.strategy_objects]

            for rule_enum in self.rule_enums:

                rule_outcome = np.all([outcome[rule_enum.value]
                                      for outcome in rule_outcome])

                if rule_outcome:
                    trade = Trade(
                        ticker, pricing_data.iloc[index], self.trade_settings)

                    try:
                        trade.execute_trade(pricing_data)
                    except Exception as e:
                        print(f"Error executing trade for ticker {ticker}")
                        raise e

                    trade.condition = rule_enum.value
                    self.trades[ticker].append(trade)
                    for strategy_object in self.strategy_objects:
                        if hasattr(strategy_object, "meta_data"):
                            self.meta_data_logger[ticker][date] = strategy_object.meta_data[index]


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
