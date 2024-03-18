from beartype.typing import List
from enum import Enum

from .indicators import calculate_ema, candle_body_outside_range, calculate_rsi


class RuleEnum(Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"


class StrategyObject:
    def __init__(self):
        self.rules = {}
        self.rules[RuleEnum.BULLISH.value] = self._evaluate_bullish_rules
        self.rules[RuleEnum.BEARISH.value] = self._evaluate_bearish_rules

    def evaluate_rules(self, index, rule_enums: List[RuleEnum] = None):
        self.index = index

        if rule_enums is None:
            rule_enums = self.rules.keys()
        else:
            rule_enums = [rule_enum.value for rule_enum in rule_enums]

        rules_outcome = {}

        for rule_enum in rule_enums:
            rules_outcome[rule_enum] = self.rules[rule_enum]()

        return rules_outcome

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data


class FIBStrategy(StrategyObject):
    strategy_name = "FIB"

    def __init__(self, percent_range: List[float]):
        super().__init__()
        self.percent_range = sorted(percent_range)
        self.indicator_keys = ["fib_bools", "fib_data"]

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

    def _evaluate_bullish_rules(self):
        if self.indicator_values["fib_bools"][self.index][1]:
            return True
        return False

    def _evaluate_bearish_rules(self):
        if not self.indicator_values["fib_bools"][self.index][0]:
            return True
        return False


class EMAStrategy(StrategyObject):
    strategy_name = "EMA"

    @classmethod
    def __init_from_id__(cls, id: str):
        periods = [int(period) for period in id.split("_")[1:]]
        rules = [rule for rule in id.split("_")[4:]]

        return EMAStrategy(periods=periods, rules=rules)

    def __init__(self,
                 periods: List[int],
                 rules: None | List[str] = None,
                 ) -> None:

        super().__init__()
        self.setup_selected_rules(rules)
        self.periods = sorted(periods)
        self.indicator_keys = [f"ema_{period}" for period in self.periods]
        self.setup_id()

    def setup_id(self):
        self.id = "ema_"
        self.id += "_".join([str(period) for period in self.periods])

        self.id += "_"
        self.id += "_".join([rule for rule in sorted(self.selected_rules.keys())])

    def setup_selected_rules(self, rules: None | List[str] = None):
        available_rules = {"fan_out":
                           {RuleEnum.BULLISH.value: self._bullish_fan_out_rule,
                            RuleEnum.BEARISH.value: self._bearish_fan_out_rule},
                           "candle":
                           {RuleEnum.BULLISH.value: self._bullish_candle_rule,
                            RuleEnum.BEARISH.value: self._bearish_candle_rule}
                           }

        if rules is None:
            rules = list(available_rules.keys())

        self.selected_rules = {}

        for rule in rules:
            if rule not in available_rules:
                raise NotImplementedError(
                    f"{rule} is not a valid rule for EMAStrategy possible rules are {list(available_rules.keys())}")
            self.selected_rules[rule] = available_rules[rule]

    def calculate_indicators(self):
        self.indicator_values = {}
        self.meta_data = {}
        for i, period in enumerate(self.periods):
            key = self.indicator_keys[i]
            self.indicator_values[key] = calculate_ema(self.data, period)

        self.meta_data = [""] * len(self.data.index)
        for date_index, date in enumerate(self.data.index):
            for i, period in enumerate(self.periods):
                key_i = self.indicator_keys[i]
                for j in range(i + 1, len(self.periods)):
                    key_j = self.indicator_keys[j]
                    ratio = self.indicator_values[key_i][date] / \
                        self.indicator_values[key_j][date]
                    #fmt: off
                    self.meta_data[date_index] += f"\t{key_i:7} / {key_j:7}: {ratio:8.2f}\n"
                    #fmt: on

    def _evaluate_bullish_rules(self):
        is_bullish = True
        for rule in self.selected_rules:
            is_bullish &= self.selected_rules[rule][RuleEnum.BULLISH.value]()

        return is_bullish

    def _evaluate_bearish_rules(self):
        is_bearish = True
        for rule in self.selected_rules:
            is_bearish &= self.selected_rules[rule][RuleEnum.BEARISH.value]()

        return is_bearish

    def _bullish_fan_out_rule(self):
        return self._fan_out_rule(lambda x, y: x > y)

    def _bearish_fan_out_rule(self):
        return self._fan_out_rule(lambda x, y: x < y)

    def _fan_out_rule(self, compare_operator):
        for i in range(len(self.periods) - 1):
            key_i = self.indicator_keys[i]
            key_j = self.indicator_keys[i + 1]
            if not compare_operator(self.indicator_values[key_i].iloc[self.index], self.indicator_values[key_j].iloc[self.index]):
                return False
        return True

    def _bullish_candle_rule(self):
        if self.data.iloc[self.index].low <= self.indicator_values[self.indicator_keys[0]].iloc[self.index]:
            return True
        return False

    def _bearish_candle_rule(self):
        if self.data.iloc[self.index].high >= self.indicator_values[self.indicator_keys[0]].iloc[self.index]:
            return True
        return False


class RSIStrategy(StrategyObject):
    strategy_name = "RSI"

    def __init__(self, period: int, overbought: int, oversold: int):
        super().__init__()
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
        self.indicator_keys = ["rsi"]

    def calculate_indicators(self):
        self.indicator_values = {}
        self.indicator_values["rsi"] = calculate_rsi(self.data, self.period)

    def _evaluate_bullish_rules(self):
        if self.indicator_values["rsi"].iloc[self.index] < self.oversold:
            return True
        return False

    def _evaluate_bearish_rules(self):
        if self.indicator_values["rsi"].iloc[self.index] > self.overbought:
            return True
        return False
