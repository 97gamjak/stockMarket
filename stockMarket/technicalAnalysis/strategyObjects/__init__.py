from .enums import RuleEnum
from ._base import StrategyObject
from .fibStrategy import FIBStrategy
from .movingAverageStrategy import EMAStrategy, SMAStrategy
from .rsiStrategy import RSIStrategy


def init_strategyObject_from_json(json_dict):
    strategy_name = json_dict["strategy_name"]
    if strategy_name == "FIB":
        return FIBStrategy.from_json(json_dict)
    elif strategy_name == "EMA":
        return EMAStrategy.from_json(json_dict)
    elif strategy_name == "SMA":
        return SMAStrategy.from_json(json_dict)
    elif strategy_name == "RSI":
        return RSIStrategy.from_json(json_dict)
    else:
        raise NotImplementedError(
            f"{strategy_name} is not a valid strategy name")
