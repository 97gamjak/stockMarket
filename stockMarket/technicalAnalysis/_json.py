import datetime as dt
import pandas as pd
import json
import pathlib

from beartype.typing import Optional, Dict, List

from .trade import Trade, TradeSettings
from .strategyObjects import StrategyObject, RuleEnum
from .strategyFileSettings import StrategyFileSettings
from stockMarket.utils.period import Period


class StrategyJSON:
    _main_json_file: str = ".strategy.json"
    _trades_json_file: Optional[str] = ".trades,json"
    _earnings_json_file: Optional[str] = ".earnings.json"
    _trade_settings_json_file: Optional[str] = ".trade_settings.json"

    @classmethod
    def _init_file_paths(cls, dir_path: pathlib.Path):
        cls.main_json_file = str(dir_path / cls._main_json_file)
        cls.trades_json_file = str(dir_path / cls._trades_json_file)
        cls.trade_settings_json_file = str(
            dir_path / cls._trade_settings_json_file)

    @classmethod
    def write(cls,
              trades: Dict[str, List[Trade]],
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
              earnings_calendar: Dict[str, List[dt.date]] = {},
              finalize_commands: Optional[List[str]] = None
              ):

        cls._init_file_paths(dir_path)

        cls._write_trades(trades)
        cls._write_earnings_calendar(earnings_calendar)
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

        cls._write_main_json()

    @classmethod
    def _write_main_json(cls):
        with open(cls.main_json_file, "w") as file:
            json.dump(cls.main_json_dict, file)

    @classmethod
    def _write_trades(cls, trades: Dict[str, List[Trade]]):
        with open(cls.trades_json_file, "w") as file:
            json.dump(cls._trades_to_json(trades), file)

    @classmethod
    def _trades_to_json(cls, trades: Dict[str, List[Trade]]):
        json_trades = {}
        for ticker, ticker_trades in trades.items():
            json_trades[ticker] = [trade.to_json() for trade in ticker_trades]

        return trades

    @classmethod
    def _write_earnings_calendar(cls, earnings_calendar: Dict[str, List[dt.date]]):
        with open(cls.earnings_json_file, "w") as file:
            json.dump(cls._earnings_calendar_to_json(earnings_calendar), file)

    @classmethod
    def _earnings_calendar_to_json(cls, earnings_calendar: Dict[str, List[dt.date]]):
        return {ticker: [date.isoformat() for date in dates] for ticker, dates in earnings_calendar.items()}

    @classmethod
    def _write_trade_settings(cls, trade_settings: TradeSettings):
        with open(cls.trade_settings_json_file, "w") as file:
            json.dump(trade_settings.to_json(), file)

    @classmethod
    def _strategy_objects_to_json(cls, strategy_objects: List[StrategyObject]):
        return [strategy_object.to_json() for strategy_object in strategy_objects]

    @classmethod
    def _rule_enums_to_json(cls, rule_enums: List[RuleEnum]):
        return [rule_enum.value for rule_enum in rule_enums]

    @classmethod
    def read(cls, dir_path: pathlib.Path):

        cls._init_file_paths(dir_path)

        cls.trades = cls._read_trades()
        cls.earnings_calendar = cls._read_earnings_calendar()
        cls.trade_settings = cls._read_trade_settings()

        cls.main_json_dict = cls._read_main_json()
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
    def _read_main_json(cls):
        with open(cls.main_json_file, "r") as file:
            return json.load(file)

    @classmethod
    def _strategy_objects_from_json(cls, json_data):
        return [StrategyObject.init_from_json(strategy_object) for strategy_object in json_data["strategy_objects"]]

    @classmethod
    def _rule_enums_from_json(cls):
        return [RuleEnum(rule_enum) for rule_enum in cls.main_json_dict["rule_enums"]]

    @classmethod
    def _file_settings_from_json(cls):
        return StrategyFileSettings.init_from_json(cls.main_json_dict["file_settings"])

    @classmethod
    def _read_trades(cls):
        with open(cls.trades_json_file, "r") as file:
            json_data = json.load(file)
            return cls._trades_from_json(json_data)

    @classmethod
    def _trades_from_json(cls, json_data):
        return {ticker: [Trade.init_from_json(trade) for trade in ticker_trades]
                for ticker, ticker_trades in json_data.items()}

    @classmethod
    def _read_earnings_calendar(cls):
        with open(cls.earnings_json_file, "r") as file:
            json_data = json.load(file)
            return cls._earnings_calendar_from_json(json_data)

    @classmethod
    def _earnings_calendar_from_json(cls, json_data):
        return {ticker: [dt.date.fromisoformat(date) for date in dates] for ticker, dates in json_data.items()}

    @classmethod
    def _read_trade_settings(cls):
        return TradeSettings().from_json_file(cls.trade_settings_json_file)
