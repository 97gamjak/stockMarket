import datetime as dt
import numpy as np
import pandas as pd
import yfinance as yf
import re
import os
import matplotlib.pyplot as plt
import inspect
import warnings

from decorator import decorator
from beartype.typing import List, Optional, Dict
from tqdm import tqdm
from finance_calendars import finance_calendars as fc
from pathlib import Path

from .strategyObjects import StrategyObject, RuleEnum
from .trade import (
    Trade,
    TradeSettings,
    TradeOutcome,
    TradeStatus,
)
from ._json import StrategyJSON
from ._common import finalize
from .strategyFileSettings import StrategyFileSettings
from .strategyXLSXWriter import StrategyXLSXWriter
from stockMarket.utils import Period
from stockMarket.yfinance._common import adjust_price_data_from_df


class Strategy:
    def __init__(self,
                 strategy_objects: List[StrategyObject],
                 start_date: str,
                 end_date: str,
                 rule_enums: List[RuleEnum] = [RuleEnum.BULLISH],
                 num_batches: int = 1,
                 batch_size: Optional[pd.Timedelta] = None,
                 trade_settings: Optional[TradeSettings] = None,
                 candle_period: str | Period | None = None,
                 use_earnings_dates: bool = False,
                 finalize_commands: Optional[List[str]] = None,
                 init_from_json: bool = False,
                 **kwargs
                 ) -> None:

        if not init_from_json:
            self.__clean_init__(
                strategy_objects,
                start_date,
                end_date,
                rule_enums,
                num_batches,
                batch_size,
                trade_settings,
                candle_period,
                use_earnings_dates,
                finalize_commands,
                **kwargs
            )
        else:
            if "dir_path" in kwargs:
                self.dir_path = Path(kwargs["dir_path"])
            elif "dir_name" in kwargs and "base_path" in kwargs:
                self.dir_path = Path(kwargs["base_path"]) / kwargs["dir_name"]
            else:
                raise ValueError(
                    "Either dir_path or dir_name and base_path must be provided in kwargs for init_from_json")

            self.__init_from_json__(self.dir_path)

    def __clean_init__(self,
                       strategy_objects: List[StrategyObject],
                       start_date: str,
                       end_date: str,
                       rule_enums: List[RuleEnum] = [RuleEnum.BULLISH],
                       num_batches: int = 1,
                       batch_size: Optional[pd.Timedelta] = None,
                       trade_settings: Optional[TradeSettings] = None,
                       candle_period: str | Period | None = None,
                       use_earnings_dates: bool = False,
                       finalize_commands: Optional[List[str]] = None,
                       **kwargs
                       ) -> None:

        self.strategy_objects = strategy_objects
        self.rule_enums = rule_enums
        self.trades: Dict[str, List[Trade]] = {}
        self.error_logger = {}
        self.use_earnings_dates = use_earnings_dates
        self.finalize_commands = finalize_commands
        self.earnings_calendar: Dict[str, List[dt.date]] = {}
        self.file_settings = None

        self.setup_files(
            self.strategy_objects,
            self.rule_enums,
            **kwargs
        )

        self.setup_dates(
            start_date,
            end_date,
            candle_period,
            num_batches,
            batch_size
        )

        self.setup_trade_settings(trade_settings)

        self.xlsx_writer = StrategyXLSXWriter(
            self.template_xlsx_file,
            self.xlsx_filename,
            self.trade_settings,
            self.candle_period,
            self.start_date,
            self.end_date,
            self.batch_size,
        )

        StrategyJSON.write(
            strategy_objects=self.strategy_objects,
            rule_enums=self.rule_enums,
            file_settings=self.file_settings,
            use_earnings_dates=self.use_earnings_dates,
            start_date=self.start_date,
            end_date=self.end_date,
            candle_period=self.candle_period,
            batch_size=self.batch_size,
            trade_settings=self.trade_settings,
            dir_path=self.dir_path,
        )

    def init_from_json(self, dir_path: Path):
        StrategyJSON.read(dir_path)

        self.file_settings = StrategyJSON.file_settings
        self._init_from_file_settings()

        self.strategy_objects = StrategyJSON.strategy_objects
        self.rule_enums = StrategyJSON.rule_enums
        self.trades = StrategyJSON.trades
        self.use_earnings_dates = StrategyJSON.use_earnings_dates
        self.earnings_calendar = StrategyJSON.earnings_calendar
        self.start_date = StrategyJSON.start_date
        self.end_date = StrategyJSON.end_date
        self.candle_period = StrategyJSON.candle_period
        self.batch_size = StrategyJSON.batch_size
        self.trade_settings = StrategyJSON.trade_settings

    def setup_files(self,
                    strategy_objects,
                    rule_enums,
                    **kwargs
                    ):
        args_of_init = inspect.getfullargspec(
            StrategyFileSettings.__init__).args

        kwargs_for_file_settings = {}
        for key, value in kwargs.items():
            if key in args_of_init:
                kwargs_for_file_settings[key] = value

        self.file_settings = StrategyFileSettings(
            **kwargs_for_file_settings
        )

        self.file_settings.setup(strategy_objects, rule_enums)
        self._init_from_file_settings()

    def _init_from_file_settings(self):

        self.dir_path = self.file_settings.dir_path
        self.template_xlsx_file = self.file_settings.template_xlsx_file
        self.xlsx_filename = self.file_settings.xlsx_filename

        self.error_logger_filename = str(self.dir_path / "error_logger.txt")

    def setup_dates(self,
                    start_date: str,
                    end_date: str,
                    candle_period: str | Period | None,
                    num_batches: int,
                    batch_size: Optional[pd.Timedelta] = None,
                    ):
        if candle_period is None:
            self.candle_period = Period('daily')
        else:
            self.candle_period = Period(candle_period)

        self.start_date, self.end_date = _check_dates(start_date, end_date)

        if batch_size is None:
            diff_dates = self.end_date - self.start_date + pd.Timedelta(days=1)
            self.batch_size = (diff_dates / num_batches).days
            self.batch_size = pd.Timedelta(days=self.batch_size)
        else:
            self.batch_size = batch_size
            if num_batches != 1:
                warnings.warn(
                    "Both num_batches and batch_size are set. num_batches will be ignored")

    def setup_trade_settings(self, trade_settings: Optional[TradeSettings] = None):
        self.trade_settings = trade_settings if trade_settings is not None else TradeSettings()

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

        StrategyJSON.write_earnings_calendar(
            dir_path=self.dir_path,
            earnings_calendar=self.earnings_calendar
        )

    @finalize
    def screen(self, tickers: List[str] | str) -> None:

        self.tickers = sorted(np.atleast_1d(tickers))

        if self.use_earnings_dates:
            self.get_earnings_dates()

        for ticker in tqdm(self.tickers):
            pricing_data = self.populate_pricing_data(ticker)
            self._screen_single_ticker(ticker, pricing_data)

        self.xlsx_writer.write_xlsx_file(self.trades, self.earnings_calendar)

        StrategyJSON.write_trades(
            trades=self.trades,
            dir_path=self.dir_path
        )

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
