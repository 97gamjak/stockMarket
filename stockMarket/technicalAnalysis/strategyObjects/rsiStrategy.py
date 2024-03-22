from beartype.typing import List

from stockMarket.technicalAnalysis.indicators import calculate_rsi
from ._base import StrategyObject
from .enums import RuleEnum


class RSIStrategy(StrategyObject):
    def __init__(self,
                 period: int,
                 overbought: int,
                 oversold: int,
                 rules: None | List[str] = None,
                 ):

        super().__init__(rules)
        self.period = period
        self.overbought = overbought
        self.oversold = oversold

    def calculate_indicators(self):
        self.indicator_values = {}
        self.indicator_values["rsi"] = calculate_rsi(self.data, self.period)

    def setup_selected_rules(self, rules: None | List[str] = None):
        self.available_rules = {"rsi":
                                {RuleEnum.BULLISH.value: self.bullish_rule,
                                 RuleEnum.BEARISH.value: self.bearish_rule},
                                }

        super().setup_selected_rules(rules)

    def bullish_rule(self):
        if self.indicator_values["rsi"].iloc[self.index] < self.oversold:
            return True
        return False

    def bearish_rule(self):
        if self.indicator_values["rsi"].iloc[self.index] > self.overbought:
            return True
        return False

    def to_json(self):
        json_dict = super().to_json()
        json_dict["period"] = self.period
        json_dict["overbought"] = self.overbought
        json_dict["oversold"] = self.oversold
        return json_dict

    @property
    def strategy_name(self):
        return "RSI"

    @property
    def indicator_keys(self):
        return ["rsi"]
