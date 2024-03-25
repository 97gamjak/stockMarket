"""
A module for reading and writing strategy objects to and from json files.
"""

import datetime as dt
import pandas as pd
import json
import pathlib

from beartype.typing import Optional, Dict, List, Any

from .trade import Trade, TradeSettings
from .strategyObjects import StrategyObject, RuleEnum
from .strategyFileSettings import StrategyFileSettings
from stockMarket.utils.period import Period


class StrategyJSON:
    """
    A class for reading and writing strategy objects to and from json files.

    This class is only used as a static class and should not be instantiated.
    """
    _main_json_file: str = ".strategy.json"
    _trades_json_file: Optional[str] = ".trades,json"
    _earnings_json_file: Optional[str] = ".earnings.json"
    _trade_settings_json_file: Optional[str] = ".trade_settings.json"

    @classmethod
    def _init_file_paths(cls, dir_path: pathlib.Path) -> None:
        """
        Function to initialize the file paths for the json files.

        At the moment all filenames are hardcoded as class variables.
        This has the advantage that the filenames are always the same and
        there can not be any mixup with the filenames.

        Parameters
        ----------
        dir_path : pathlib.Path
            The directory path where the json files are stored.
        """
        cls.main_json_file = str(dir_path / cls._main_json_file)
        cls.trades_json_file = str(dir_path / cls._trades_json_file)
        cls.earnings_json_file = str(dir_path / cls._earnings_json_file)
        cls.trade_settings_json_file = str(
            dir_path / cls._trade_settings_json_file)

    @classmethod
    def write(cls,
              strategy_objects: List[StrategyObject],
              rule_enums: List[RuleEnum],
              start_date: dt.date,
              end_date: dt.date,
              candle_period: Period,
              batch_size: pd.Timedelta,
              file_settings: StrategyFileSettings,
              trade_settings: TradeSettings,
              dir_path: pathlib.Path,
              use_earnings_dates: bool,
              finalize_commands: Optional[List[str]] = None
              ) -> None:
        """
        Function to write a strategy to a json file

        Parameters
        ----------
        strategy_objects : List[StrategyObject]
            A list of strategy objects that are used in the strategy.
        rule_enums : List[RuleEnum]
            A list of rule enums that are used in the strategy.
        start_date : dt.date
            The start date of the strategy.
        end_date : dt.date
            The end date of the strategy.
        candle_period : Period
            The candle period of the strategy.
        batch_size : pd.Timedelta
            The batch size of the date range that is processed in one batch.
        file_settings : StrategyFileSettings
            The file settings of the strategy.
        trade_settings : TradeSettings
            The trade settings of the strategy.
        dir_path : pathlib.Path
            The directory path where the json files are stored.
        use_earnings_dates : bool
            A boolean that indicates if the earnings dates should be used.
        finalize_commands : Optional[List[str]]
            A list of commands that are executed after the strategy has been processed.
        """

        cls._init_file_paths(dir_path)

        cls._write_trade_settings(trade_settings)

        cls.main_json_dict = {}
        cls.main_json_dict["strategy_objects"] = cls._strategy_objects_to_json(
            strategy_objects)
        cls.main_json_dict["rule_enums"] = cls._rule_enums_to_json(rule_enums)
        cls.main_json_dict["file_settings"] = file_settings.to_json()
        cls.main_json_dict["use_earnings_dates"] = use_earnings_dates
        cls.main_json_dict["finalize_commands"] = finalize_commands
        cls.main_json_dict["start_date"] = start_date.isoformat()
        cls.main_json_dict["end_date"] = end_date.isoformat()
        cls.main_json_dict["candle_period"] = candle_period.period_string
        cls.main_json_dict["batch_size"] = batch_size.total_seconds()

        cls._write_strategy_json()

    @classmethod
    def _write_strategy_json(cls) -> None:
        """
        Function to write the strategy json to a file.
        """
        with open(cls.main_json_file, "w") as file:
            json.dump(cls.main_json_dict, file)

    @classmethod
    def write_trades(cls,
                     trades: Dict[str, List[Trade]],
                     dir_path: pathlib.Path,
                     ) -> None:
        """
        Function to write all trades from a strategy to a json file.

        Parameters
        ----------
        trades : Dict[str, List[Trade]]
            A dictionary with the ticker as key and a list of trades as value.
        dir_path : pathlib.Path
            The directory path where the json files are stored.
        """

        cls._init_file_paths(dir_path)

        with open(cls.trades_json_file, "w") as file:
            json.dump(cls._trades_to_json(trades), file)

    @classmethod
    def _trades_to_json(cls,
                        trades: Dict[str, List[Trade]]
                        ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Function to convert trades to a json serializable format.

        Parameters
        ----------
        trades : Dict[str, List[Trade]]
            A dictionary with the ticker as key and a list of trades as value.

        Returns
        -------
        Dict[str, List[Dict[str, Any]]]
            A dictionary with the ticker as key and a list of json serializable trades as value.
        """
        json_trades = {}
        for ticker, ticker_trades in trades.items():
            json_trades[ticker] = [trade.to_json() for trade in ticker_trades]

        return trades

    @classmethod
    def write_earnings_calendar(cls,
                                earnings_calendar: Dict[str, List[dt.date]],
                                dir_path: pathlib.Path,
                                ) -> None:
        """
        Function to write the earnings calendar to a json file.

        Parameters
        ----------
        earnings_calendar : Dict[str, List[dt.date]]
            A dictionary with the ticker as key and a list of earnings dates as value.
        dir_path : pathlib.Path
            The directory path where the json files are stored.
        """

        cls._init_file_paths(dir_path)

        with open(cls.earnings_json_file, "w") as file:
            json.dump(cls._earnings_calendar_to_json(earnings_calendar), file)

    @classmethod
    def _earnings_calendar_to_json(cls,
                                   earnings_calendar: Dict[str, List[dt.date]]
                                   ) -> Dict[str, List[str]]:
        """
        Function to convert the earnings calendar to a json serializable format.

        Parameters
        ----------
        earnings_calendar : Dict[str, List[dt.date]]
            A dictionary with the ticker as key and a list of earnings dates as value.

        Returns
        -------
        Dict[str, List[str]]
            A dictionary with the ticker as key and a list of earnings dates as string isoformat as value.
        """
        return {ticker: [date.isoformat() for date in dates] for ticker, dates in earnings_calendar.items()}

    @classmethod
    def _write_trade_settings(cls, trade_settings: TradeSettings):
        """
        Function to write the trade settings to a json file.

        Parameters
        ----------
        trade_settings : TradeSettings
            The trade settings that should be written to a json file.
        """
        with open(cls.trade_settings_json_file, "w") as file:
            json.dump(trade_settings.to_json(), file)

    @classmethod
    def _strategy_objects_to_json(cls,
                                  strategy_objects: List[StrategyObject]
                                  ) -> List[Dict[str, Any]]:
        """
        Function to convert list strategy objects to a json serializable format.

        Parameters
        ----------
        strategy_objects : List[StrategyObject]
            A list of strategy objects that should be converted to a json serializable format.

        Returns
        -------
        List[Dict[str, Any]]
            A list of json serializable strategy objects.
        """
        return [strategy_object.to_json() for strategy_object in strategy_objects]

    @classmethod
    def _rule_enums_to_json(cls,
                            rule_enums: List[RuleEnum]
                            ) -> List[str]:
        """
        Function to convert list of rule enums to a json serializable format.

        Parameters
        ----------
        rule_enums : List[RuleEnum]
            A list of rule enums that should be converted to a json serializable format.

        Returns
        -------
        List[str]
            A list of rule enums as strings.
        """
        return [rule_enum.value for rule_enum in rule_enums]

    @classmethod
    def read(cls, dir_path: pathlib.Path) -> None:
        """
        Function to read the strategy json files.

        It processes the main json file and reads the trades, earnings calendar and trade settings.

        Parameters
        ----------
        dir_path : pathlib.Path
            The directory path where the json files are stored.
        """

        cls._init_file_paths(dir_path)

        cls.trades = cls._read_trades()
        cls.earnings_calendar = cls._read_earnings_calendar()
        cls.trade_settings = cls._read_trade_settings()

        cls.main_json_dict = cls._read_strategy_json()
        cls.strategy_objects = cls._strategy_objects_from_json()
        cls.rule_enums = cls._rule_enums_from_json()
        cls.file_settings = cls._file_settings_from_json()
        cls.use_earnings_dates = cls.main_json_dict["use_earnings_dates"]
        cls.finalize_commands = cls.main_json_dict["finalize_commands"]
        cls.start_date = dt.date.fromisoformat(
            cls.main_json_dict["start_date"])
        cls.end_date = dt.date.fromisoformat(cls.main_json_dict["end_date"])
        cls.candle_period = Period(cls.main_json_dict["candle_period"])
        cls.batch_size = pd.Timedelta(seconds=cls.main_json_dict["batch_size"])

    @classmethod
    def _read_strategy_json(cls):
        """
        Function to read the main json file.

        Returns
        -------
        Dict[str, Any]
            The main json file as a dictionary.
        """
        with open(cls.main_json_file, "r") as file:
            return json.load(file)

    @classmethod
    def _strategy_objects_from_json(cls) -> List[StrategyObject]:
        """
        Function to convert the strategy objects from the main json file to a list of strategy objects.

        Returns
        -------
        List[StrategyObject]
            A list of strategy objects.
        """
        return [StrategyObject.init_from_json(strategy_object) for strategy_object in cls.main_json_file["strategy_objects"]]

    @classmethod
    def _rule_enums_from_json(cls) -> List[RuleEnum]:
        """
        Function to convert the rule enums from the main json file to a list of rule enums.

        Returns
        -------
        List[RuleEnum]
            A list of rule enums.
        """
        return [RuleEnum(rule_enum) for rule_enum in cls.main_json_dict["rule_enums"]]

    @classmethod
    def _file_settings_from_json(cls) -> StrategyFileSettings:
        """
        Function to convert the file settings from the main json file to a StrategyFileSettings object.

        Returns
        -------
        StrategyFileSettings
            The file settings as a StrategyFileSettings object.
        """
        return StrategyFileSettings.init_from_json(cls.main_json_dict["file_settings"])

    @classmethod
    def _read_trades(cls) -> Dict[str, List[Trade]]:
        """
        Function to read the trades from a json file.

        Returns
        -------
        Dict[str, List[Trade]]
            A dictionary with the ticker as key and a list of trade objects as value.
        """
        with open(cls.trades_json_file, "r") as file:
            json_data = json.load(file)
            return cls._trades_from_json(json_data)

    @classmethod
    def _trades_from_json(cls,
                          json_data: Dict[str, List[Dict[str, Any]]]
                          ) -> Dict[str, List[Trade]]:
        """
        Function to convert the trades from a json serializable format to a dictionary with ticker as key and a list of trade objects as value.

        Parameters
        ----------
        json_data : Dict[str, List[Dict[str, Any]]]
            A dictionary with the ticker as key and a list of json serializable trades as value.

        Returns
        -------
        Dict[str, List[Trade]]
            A dictionary with the ticker as key and a list of trade objects as value.
        """
        return {ticker: [Trade.init_from_json(trade) for trade in ticker_trades]
                for ticker, ticker_trades in json_data.items()}

    @classmethod
    def _read_earnings_calendar(cls) -> Dict[str, List[dt.date]]:
        """
        Function to read the earnings calendar from a json file.

        Returns
        -------
        Dict[str, List[dt.date]]
            A dictionary with the ticker as key and a list of earnings dates as value.
        """
        with open(cls.earnings_json_file, "r") as file:
            json_data = json.load(file)
            return cls._earnings_calendar_from_json(json_data)

    @classmethod
    def _earnings_calendar_from_json(cls,
                                     json_data: Dict[str, List[str]]
                                     ) -> Dict[str, List[dt.date]]:
        """
        Function to convert the earnings calendar from a json serializable format to a dictionary with ticker as key and a list of earnings dates as value.

        Parameters
        ----------
        json_data : Dict[str, List[str]]
            A dictionary with the ticker as key and a list of earnings dates as string isoformat as value.

        Returns
        -------
        Dict[str, List[dt.date]]
            A dictionary with the ticker as key and a list of earnings dates as value.
        """
        return {ticker: [dt.date.fromisoformat(date) for date in dates] for ticker, dates in json_data.items()}

    @classmethod
    def _read_trade_settings(cls) -> TradeSettings:
        """
        Function to read the trade settings from a json file.

        Returns
        -------
        TradeSettings
            The trade settings as a TradeSettings object.
        """
        return TradeSettings().from_json_file(cls.trade_settings_json_file)
