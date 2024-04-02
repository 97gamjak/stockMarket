import pandas as pd

from beartype.typing import List

from ._base import StrategyObject
from .enums import RuleEnum
from stockMarket.technicalAnalysis.indicators import candle_body_outside_range


class FIBStrategy(StrategyObject):
    @classmethod
    def init_from_json(cls, json_dict):
        return cls(json_dict["percent_range"], json_dict["rules"])

    def __init__(self,
                 percent_range: List[float],
                 rules: None | List[str] = None,
                 ):
        super().__init__(rules)
        self.percent_range = sorted(percent_range)

    def calculate_indicators(self):
        def apply_candle_body_outside_range(row):
            fib_bools_i, fib_data_i = candle_body_outside_range(
                row, self.percent_range)
            return pd.Series([fib_bools_i, fib_data_i])

        result = self.data.apply(apply_candle_body_outside_range, axis=1)
        fib_bools = result[0].tolist()
        fib_data = result[1].tolist()

        self.indicator_values = {"fib_bools": fib_bools, "fib_data": fib_data}

    def setup_selected_rules(self, rules: None | List[str] = None):
        self.available_rules = {"fib_bools":
                                {RuleEnum.BULLISH.value: self.bullish_rule,
                                 RuleEnum.BEARISH.value: self.bearish_rule},
                                }

        super().setup_selected_rules(rules)

    def bullish_rule(self):
        if self.indicator_values["fib_bools"][self.index][1]:
            return True
        return False

    def bearish_rule(self):
        if not self.indicator_values["fib_bools"][self.index][0]:
            return True
        return False

    def to_json(self):
        json_dict = super().to_json()
        json_dict["percent_range"] = self.percent_range
        return json_dict

    @property
    def strategy_name(self):
        return "FIB"

    @property
    def indicator_keys(self):
        return ["fib_bools", "fib_data"]
