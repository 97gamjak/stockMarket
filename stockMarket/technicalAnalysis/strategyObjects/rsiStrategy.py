from beartype.typing import List

from stockMarket.technicalAnalysis.indicators import calculate_rsi
from ._base import StrategyObject
from .enums import RuleEnum


class RSIStrategy(StrategyObject):
    strategy_name = "RSI"

    @classmethod
    def init_from_id(cls, id: str):
        period, overbought, oversold = [
            int(value) for value in id.split("_")[1:4]]
        rules = [rule for rule in id.split("_")[4:]]

        return RSIStrategy(
            period=period,
            overbought=overbought,
            oversold=oversold,
            rules=rules
        )

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
        self.indicator_keys = ["rsi"]

    def setup_id(self):
        self.id = "rsi_"
        self.id += str(self.period)
        self.id += "_"
        self.id += str(self.overbought)
        self.id += "_"
        self.id += str(self.oversold)
        self.id += "_"
        self.id += "_".join([rule for rule in sorted(self.selected_rules.keys())])

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
