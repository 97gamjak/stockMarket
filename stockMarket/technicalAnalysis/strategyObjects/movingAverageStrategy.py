from beartype.typing import List
from abc import ABCMeta, abstractmethod

from .enums import RuleEnum
from ._base import StrategyObject
from stockMarket.technicalAnalysis.indicators import calculate_ema, calculate_sma


class MovingAverageStrategy(StrategyObject, metaclass=ABCMeta):
    @classmethod
    def init_from_id(cls, id: str):
        periods = [int(period) for period in id.split("_")[1:]]
        rules = [rule for rule in id.split("_")[4:]]

        if id.startswith("ema"):
            return EMAStrategy(periods=periods, rules=rules)
        else:
            return SMAStrategy(periods=periods, rules=rules)

    @abstractmethod
    def __init__(self,
                 periods: List[int],
                 rules: None | List[str] = None,
                 ) -> None:

        StrategyObject.__init__(self, rules)
        self.periods = sorted(periods)
        self.setup_id()

    @abstractmethod
    def setup_id(self):
        self.id = "_".join([str(period) for period in self.periods])
        self.id += "_"
        self.id += "_".join([rule for rule in sorted(self.selected_rules.keys())])

    def setup_selected_rules(self, rules: None | List[str] = None):
        self.available_rules = {"fan_out":
                                {RuleEnum.BULLISH.value: self._bullish_fan_out_rule,
                                 RuleEnum.BEARISH.value: self._bearish_fan_out_rule},
                                "candle":
                                {RuleEnum.BULLISH.value: self._bullish_candle_rule,
                                    RuleEnum.BEARISH.value: self._bearish_candle_rule}
                                }

        super().setup_selected_rules(rules)

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


class EMAStrategy(MovingAverageStrategy):
    strategy_name = "EMA"

    def __init__(self,
                 periods: List[int],
                 rules: None | List[str] = None,
                 ) -> None:

        MovingAverageStrategy.__init__(self, periods, rules)
        self.indicator_keys = [f"ema_{period}" for period in self.periods]

    def setup_id(self):
        super().setup_id()
        self.id = "ema_" + self.id

    def calculate_indicators(self):
        self.indicator_values = {}
        for i, period in enumerate(self.periods):
            key = self.indicator_keys[i]
            self.indicator_values[key] = calculate_ema(self.data, period)


class SMAStrategy(MovingAverageStrategy):
    strategy_name = "SMA"

    def __init__(self,
                 periods: List[int],
                 rules: None | List[str] = None,
                 ) -> None:

        MovingAverageStrategy.__init__(self, periods, rules)
        self.indicator_keys = [f"sma_{period}" for period in self.periods]

    def setup_id(self):
        super().setup_id()
        self.id = "sma_" + self.id

    def calculate_indicators(self):
        self.indicator_values = {}
        for i, period in enumerate(self.periods):
            key = self.indicator_keys[i]
            self.indicator_values[key] = calculate_sma(self.data, period)
