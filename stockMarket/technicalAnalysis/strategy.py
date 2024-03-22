import datetime as dt
import numpy as np
import pandas as pd
import yfinance as yf
import re
import os
import matplotlib.pyplot as plt
import inspect
import warnings
import json

from decorator import decorator
from beartype.typing import List, Optional, Dict
from tqdm import tqdm
from finance_calendars import finance_calendars as fc

from .strategyObjects import StrategyObject, RuleEnum
from .trade import (
    Trade,
    TradeSettings,
    TradeOutcome,
    TradeStatus,
)
from .strategyFileSettings import StrategyFileSettings
from .strategyXLSXWriter import StrategyXLSXWriter
from stockMarket.utils import Period
from stockMarket.yfinance._common import adjust_price_data_from_df


@decorator
def finalize(func, *args, **kwargs):
    self = args[0]
    func(*args, **kwargs)

    finalize_commands = np.atleast_1d(
        self.finalize_commands) if self.finalize_commands is not None else []

    for command in finalize_commands:
        os.system(command)


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
                 finalize_commands=None,
                 **kwargs
                 ) -> None:

        self.strategy_objects = strategy_objects
        self.rule_enums = rule_enums
        self.trades: Dict[str, List[Trade]] = {}
        self.error_logger = {}
        self.use_earnings_dates = use_earnings_dates
        self.finalize_commands = finalize_commands
        self.earnings_calendar = {}

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
            self.start_date,
            self.end_date,
            self.batch_size,
        )

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

        file_settings = StrategyFileSettings(
            **kwargs_for_file_settings
        )

        file_settings.setup(strategy_objects, rule_enums)

        self.dir_path = file_settings.dir_path
        self.template_xlsx_file = file_settings.template_xlsx_file
        self.xlsx_filename = file_settings.xlsx_filename
        self.json_file = file_settings.json_file
        self.trades_json_file = file_settings.trades_json_file

        self.trade_settings_file = str(self.dir_path / "trade_settings.json")
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

        self.trade_settings.write_to_json_file(self.trade_settings_file)

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

    @finalize
    def screen(self, tickers: List[str] | str) -> None:

        self.tickers = sorted(np.atleast_1d(tickers))

        if self.use_earnings_dates:
            self.get_earnings_dates()

        for ticker in tqdm(self.tickers):
            pricing_data = self.populate_pricing_data(ticker)
            self._screen_single_ticker(ticker, pricing_data)

        self.xlsx_writer.write_xlsx_file(self.trades, self.earnings_calendar)

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

    @finalize
    def plot_PL_histogram(self):
        PL_win_values = []
        PL_loss_values = []
        for trades in self.trades.values():
            for trade in trades:
                if trade.outcome_status == TradeOutcome.WIN:
                    PL_win_values.append(trade.PL)
                elif trade.outcome_status == TradeOutcome.LOSS:
                    PL_loss_values.append(trade.PL)

        # Define the bins
        bins = np.arange(0, 6, 0.25)

        # Calculate the counts of 'win' and 'loss' trades in each bin
        win_counts, _ = np.histogram(PL_win_values, bins=bins)
        loss_counts, _ = np.histogram(PL_loss_values, bins=bins)

        # Calculate the PL ratio for each bin
        PL_ratio = win_counts / (win_counts + loss_counts)

        # Create a figure and a subplot
        _, ax1 = plt.subplots()

        # Plot the histogram on ax1
        ax1.hist([PL_win_values, PL_loss_values], bins=bins, alpha=0.5,
                 label=['win', 'loss'], stacked=True, color=["g", "r"])
        ax1.legend(loc='upper left')

        # Create a second y-axis
        ax2 = ax1.twinx()

        # Plot the PL ratio on ax2
        ax2.plot(bins[:-1], PL_ratio, color='k', label='PL ratio')
        ax2.legend(loc='upper right')
        ax2.set_ylim(0, 1)

        plt.savefig(str(self.dir_path / "PL_histogram.png"))

    @finalize
    def plot_trades_vs_time(self, max_loss=1):
        days = []
        amount_trades = []
        total_invested = []
        total_outcome = []
        day = self.start_date
        max_exit_date = self.start_date
        while day < pd.Timestamp.now().date():
            amount_trades.append(0)
            total_invested.append(0)
            total_outcome.append(0)
            days.append(day)
            for trades in self.trades.values():
                for trade in trades:
                    if trade.trade_status not in [TradeStatus.OPEN, TradeStatus.CLOSED]:
                        continue

                    if trade.trade_status == TradeStatus.CLOSED:
                        if trade.EXIT_date == day:
                            total_outcome[-1] += trade.OUTCOME*max_loss

                    if trade.ENTRY_date <= day:
                        if trade.trade_status == TradeStatus.OPEN or trade.EXIT_date >= day:
                            amount_trades[-1] += 1
                            total_invested[-1] += trade.INVESTMENT*max_loss

                    if trade.EXIT_date is not None:
                        max_exit_date = max(max_exit_date, trade.EXIT_date)

            day += pd.Timedelta(days=1)

        days = [day for day in days if day <= max_exit_date]
        amount_trades = amount_trades[:len(days)]
        total_invested = total_invested[:len(days)]
        total_outcome = total_outcome[:len(days)]

        _, ax = plt.subplots(1, 3, figsize=(30, 10))

        ax[0].plot(days, amount_trades)
        ax[0].set_xlabel("Date", fontsize=18)
        ax[0].set_ylabel("Amount of trades", fontsize=18)

        ax[1].plot(days, total_invested, color="r")
        ax[1].set_ylabel("Total Invested in $", fontsize=18)
        ax[1].set_xlabel("Date", fontsize=18)

        ax[2].plot(
            days,
            np.cumsum(total_outcome),
            color="g",
            label="Forward Total Outcome",
            fontsize=18
        )
        ax[2].plot(
            days,
            np.cumsum(total_outcome[::-1]),
            color="b",
            label="Backward Total Outcome",
            fontsize=18
        )
        ax[2].set_ylabel("Total Outcome in $", fontsize=18)
        ax[2].set_xlabel("Date", fontsize=18)
        ax[2].legend(loc="upper left")

        # make figure more compact
        plt.tight_layout()
        plt.savefig(str(self.dir_path / "trades_vs_time.png"))

    def trades_to_json(self):
        trades = {}
        for ticker, ticker_trades in self.trades.items():
            trades[ticker] = [trade.to_json() for trade in ticker_trades]

        return trades

    def write_trades_to_json_file(self):
        with open(self.trades_json_file, "w") as file:
            json.dump(self.trades_to_json(), file)


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
