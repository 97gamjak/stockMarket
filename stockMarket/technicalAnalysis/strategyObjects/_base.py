from .enums import RuleEnum
from beartype.typing import List
from abc import ABCMeta, abstractmethod


class StrategyObject(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def init_from_json(cls, json_data):
        pass

    @abstractmethod
    def __init__(self, rules):
        self.rules = {}
        self.rules[RuleEnum.BULLISH.value] = self._evaluate_bullish_rules
        self.rules[RuleEnum.BEARISH.value] = self._evaluate_bearish_rules
        self.setup_selected_rules(rules)

    @abstractmethod
    def calculate_indicators(self):
        pass

    @abstractmethod
    def setup_selected_rules(self, rules: None | List[str] = None):
        if rules is None:
            rules = list(self.available_rules.keys())

        self.selected_rules = {}

        for rule in rules:
            if rule not in self.available_rules:
                raise NotImplementedError(
                    f"{rule} is not a valid rule for {self.strategy_name}-Strategy possible rules are {list(self.available_rules.keys())}")
            self.selected_rules[rule] = self.available_rules[rule]

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

    @abstractmethod
    def to_json(self):

        return {"rules": self.selected_rules_to_json(), "strategy_name": self.strategy_name, "indicator_keys": self.indicator_keys}

    def selected_rules_to_json(self):
        return [rule_key for rule_key in self.selected_rules.keys()]

    @property
    @abstractmethod
    def strategy_name(self):
        pass

    @property
    @abstractmethod
    def indicator_keys(self):
        pass

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data
