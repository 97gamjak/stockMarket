from beartype.typing import List

from ._base import StrategyObject
from .enums import RuleEnum
from stockMarket.technicalAnalysis.indicators import candle_body_outside_range


class FIBStrategy(StrategyObject):
    strategy_name = "FIB"

    @classmethod
    def init_from_id(cls, id: str):
        percentages = [float(percent) for percent in id.split("_")[1:]]
        rules = [rule for rule in id.split("_")[4:]]

        return FIBStrategy(percent_range=percentages, rules=rules)

    def __init__(self,
                 percent_range: List[float],
                 rules: None | List[str] = None,
                 ):
        super().__init__(rules)
        self.percent_range = sorted(percent_range)
        self.indicator_keys = ["fib_bools", "fib_data"]

    def setup_id(self):
        self.id = "fib_"
        self.id += "_".join([str(percent) for percent in self.percent_range])
        self.id += "_"
        self.id += "_".join([rule for rule in sorted(self.selected_rules.keys())])

    def calculate_indicators(self):
        fib_bools = []
        fib_data = []
        for index in range(len(self.data)):
            candle = self.data.iloc[index]
            fib_bools_i, fib_data_i = candle_body_outside_range(
                candle, self.percent_range)
            fib_bools.append(fib_bools_i)
            fib_data.append(fib_data_i)

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
