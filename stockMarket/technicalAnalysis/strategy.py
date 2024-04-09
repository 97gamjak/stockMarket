import datetime as dt
import numpy as np
import pandas as pd
import re
import inspect
import warnings

from beartype.typing import List, Optional, Dict, Tuple
from tqdm import tqdm
from finance_calendars import finance_calendars as fc
from pathlib import Path

import stockMarket.technicalAnalysis.io.decorators as decorators

from .strategyObjects import StrategyObject, RuleEnum
from .trade import (
    Trade,
    TradeSettings,
)
from ._json import StrategyJSON
from ._common import finalize
from .strategyFileSettings import StrategyFileSettings
from .strategyXLSXWriter import StrategyXLSXWriter
from .analysis.strategyAnalysis import StrategyAnalysis
from stockMarket.utils import Period
from stockMarket.yfinance._common import get_weekly_candle_range, get_daily_candle_range


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
        """
        The strategy class is used to screen a list of tickers for trades based on a list of strategy objects. The strategy objects are used to evaluate the rules for each ticker and the trades are executed based on the outcome of the rules. The trades are stored in a dictionary with the ticker as the key and a list of trades as the value. The trades are then written to an xlsx file.

        In general, the strategy class can be initialized in two ways:
        1. By providing all the necessary parameters to the __init__ method.
        2. By providing the dir_path to the directory where the json files are stored. The json files are used to initialize the strategy class. (This setting is useful when the screening was already performed and the trades are to be analyzed or the screening is to be continued.)

        Parameters
        ----------
        strategy_objects : List[StrategyObject]
            A list of strategy objects that are used to evaluate the rules for each ticker.
        start_date : str
            The start date for the screening in the format "dd.mm.yyyy".
        end_date : str
            The end date for the screening in the format "dd.mm.yyyy".
        rule_enums : List[RuleEnum], optional
            A list of rule enums that are used to evaluate the rules for each ticker, by default [RuleEnum.BULLISH]
        num_batches : int, optional
            The number of batches to split the screening into, by default 1
        batch_size : Optional[pd.Timedelta], optional
            The size of each batch, by default None
            If None, the batch size is calculated based on the number of batches and the start and end date. If both num_batches and batch_size are provided, num_batches will be ignored.
        trade_settings : Optional[TradeSettings], optional
            The trade settings that are used to execute the trades, by default None
        candle_period : str | Period | None, optional
            The candle period for the pricing data, by default None (daily candle period is used)
        use_earnings_dates : bool, optional
            A boolean indicating whether the earnings dates should be used to filter the trades, by default False
        finalize_commands : Optional[List[str]], optional
            A list of shell commands that are executed after the screening is finished, by default None
        init_from_json : bool, optional
            A boolean indicating whether the strategy class should be initialized from a json file, by default False

        Raises
        ------
        ValueError
            init_from_json is True and neither dir_path nor the combination of dir_name and base_path is provided in kwargs.
        """

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
        """
        Initialize the strategy class by providing all the necessary parameters.

        Parameters
        ----------
        strategy_objects : List[StrategyObject]
            A list of strategy objects that are used to evaluate the rules for each ticker.
        start_date : str
            The start date for the screening in the format "dd.mm.yyyy".
        end_date : str
            The end date for the screening in the format "dd.mm.yyyy".
        rule_enums : List[RuleEnum], optional
            A list of rule enums that are used to evaluate the rules for each ticker, by default [RuleEnum.BULLISH]
        num_batches : int, optional
            The number of batches to split the screening into, by default 1
        batch_size : Optional[pd.Timedelta], optional
            The size of each batch, by default None
            If None, the batch size is calculated based on the number of batches and the start and end date. If both num_batches and batch_size are provided, num_batches will be ignored.
        trade_settings : Optional[TradeSettings], optional
            The trade settings that are used to execute the trades, by default None
        candle_period : str | Period | None, optional
            The candle period for the pricing data, by default None (daily candle period is used)
        use_earnings_dates : bool, optional
            A boolean indicating whether the earnings dates should be used to filter the trades, by default False
        finalize_commands : Optional[List[str]], optional
            A list of shell commands that are executed after the screening is finished, by default None
        """

        self.strategy_objects = strategy_objects
        self.rule_enums = rule_enums
        self.trades = pd.DataFrame()
        self.trade_objects = []
        self.error_logger = {}
        self.use_earnings_dates = use_earnings_dates
        self.finalize_commands = finalize_commands
        self.earnings_calendar: Dict[str, List[dt.date]] = {}
        self.file_settings = None

        # setup files including creating the directory
        # all input parameters used for the setup have to be given as kwargs
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

    def __init_from_json__(self, dir_path: Path):
        """
        Initialize the strategy class from a json file.

        Parameters
        ----------
        dir_path : Path
            The directory path where the json file(s) is/are stored.
        """
        StrategyJSON.read(dir_path)

        self.file_settings = StrategyJSON.file_settings
        self._init_from_file_settings()

        self.strategy_objects = StrategyJSON.strategy_objects
        self.rule_enums = StrategyJSON.rule_enums

        self.trade_objects = StrategyJSON.trades
        self.trades = pd.DataFrame(
            [
                trade.trade_dictionary
                for trade in self.trade_objects
            ]
        )

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
        """
        Setup the dates for the screening.

        Parameters
        ----------
        start_date : str
            start date in the format "dd.mm.yyyy"
        end_date : str
            end date in the format "dd.mm.yyyy"
        candle_period : str | Period | None
            candle period for the pricing data, by default None (daily candle period is used)
        num_batches : int
            number of batches to split the screening into
        batch_size : Optional[pd.Timedelta], optional
            size of each batch, by default None (calculated based on the number of batches and the start and end date). If both num_batches and batch_size are provided, num_batches will be ignored.

        Warnings
        --------
        If both num_batches and batch_size are set, num_batches will be ignored.
        """
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
        """
        Setup the trade settings for the trades.

        Parameters
        ----------
        trade_settings : Optional[TradeSettings], optional
            trade settings for the trades, by default None
        """
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

    @decorators.timeit
    @finalize
    def screen(self, tickers: List[str] | str) -> None:

        self.tickers = sorted(np.atleast_1d(tickers))

        if self.use_earnings_dates:
            self.get_earnings_dates()

        for ticker in tqdm(self.tickers):
            pricing, pricing_daily = self.populate_pricing_data(ticker)
            self._screen_single_ticker(ticker, pricing, pricing_daily)

        self.trades = pd.DataFrame(
            [
                trade.trade_dictionary
                for trade in self.trade_objects
            ]
        )

        self.xlsx_writer.write_xlsx_file(
            StrategyAnalysis(self.trades),
            self.earnings_calendar
        )

        StrategyJSON.write_trades(
            trades=self.trade_objects,
            dir_path=self.dir_path
        )

    def populate_pricing_data(self,
                              ticker: str
                              ) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:

        error_file = open(self.error_logger_filename, "w")

        start_date = pd.Timestamp(self.start_date).date()
        start_date -= pd.Timedelta(days=100 *
                                   self.candle_period.period_time.days)

        pricing_daily = get_daily_candle_range(
            ticker=ticker,
            start_date=start_date
        )

        if self.candle_period.yf_interval == "1d":
            pricing = pricing_daily.copy()
        elif self.candle_period.yf_interval == "1wk":
            pricing = get_weekly_candle_range(
                ticker=ticker,
                start_date=start_date,
                pricing_data=pricing_daily,
            )
        else:
            raise NotImplementedError("Candle period not supported yet")

        try:
            for strategy_object in self.strategy_objects:
                strategy_object.data = pricing
                strategy_object.calculate_indicators()
        except Exception as e:
            self.error_logger[ticker] = e
            error_file.write(f"Ticker: {ticker}\n")
            error_file.write(f"{self.error_logger[ticker]}\n")
            error_file.write("\n")
            error_file.flush()

            return None, None

        return pricing, pricing_daily

    def _screen_single_ticker(self,
                              ticker: str,
                              pricing: pd.DataFrame,
                              pricing_daily: pd.DataFrame,
                              ) -> None:

        if pricing is None:
            return

        end_index = _calculate_end_date_index(
            pricing,
            self.end_date
        )

        for index in -np.arange(end_index, len(pricing) + 1):
            date = get_date_from_pricing_data(pricing, index)

            if pd.Timestamp(self.start_date).date() > date:
                break

            date = pricing.iloc[index].name

            rule_outcome = [strategy_object.evaluate_rules(
                index) for strategy_object in self.strategy_objects]

            for rule_enum in self.rule_enums:

                rule_outcome = np.all([outcome[rule_enum.value]
                                      for outcome in rule_outcome])

                if rule_outcome:
                    trade = Trade(
                        ticker, pricing.iloc[index], self.trade_settings)

                    try:
                        trade.execute_trade(
                            pricing,
                            pricing_daily
                        )
                    except Exception as e:
                        print(f"Error executing trade for ticker {ticker}")
                        raise e

                    self.trade_objects.append(trade)


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
