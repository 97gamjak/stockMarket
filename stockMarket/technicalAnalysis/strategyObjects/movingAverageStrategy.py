from beartype.typing import List
from abc import ABCMeta, abstractmethod

from .enums import RuleEnum
from ._base import StrategyObject
from stockMarket.technicalAnalysis.indicators import calculate_ema, calculate_sma


class MovingAverageStrategy(StrategyObject, metaclass=ABCMeta):
    @classmethod
    def from_json(cls, json_dict):
        return cls(json_dict["periods"], json_dict["rules"])

    @abstractmethod
    def __init__(self,
                 periods: List[int],
                 rules: None | List[str] = None,
                 ) -> None:

        StrategyObject.__init__(self, rules)
        self.periods = sorted(periods)

    def setup_selected_rules(self, rules: None | List[str] = None):
        self.available_rules = {"fan_out":
                                {RuleEnum.BULLISH.value: self._bullish_fan_out_rule,
                                 RuleEnum.BEARISH.value: self._bearish_fan_out_rule},
                                "candle":
                                {RuleEnum.BULLISH.value: self._bullish_candle_rule,
                                    RuleEnum.BEARISH.value: self._bearish_candle_rule}
                                }

        super().setup_selected_rules(rules)

    @abstractmethod
    def calculate_indicators(self):
        pass

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

    def to_json(self):
        json_dict = super().to_json()
        json_dict["periods"] = self.periods
        return json_dict

    @property
    @abstractmethod
    def strategy_name(self):
        pass

    @property
    @abstractmethod
    def indicator_keys(self):
        pass


class EMAStrategy(MovingAverageStrategy):
    def __init__(self,
                 periods: List[int],
                 rules: None | List[str] = None,
                 ) -> None:

        MovingAverageStrategy.__init__(self, periods, rules)

    def calculate_indicators(self):
        self.indicator_values = {}
        for i, period in enumerate(self.periods):
            key = self.indicator_keys[i]
            self.indicator_values[key] = calculate_ema(self.data, period)

    @property
    def strategy_name(self):
        return "EMA"

    @property
    def indicator_keys(self):
        return [f"ema_{period}" for period in self.periods]


class SMAStrategy(MovingAverageStrategy):
    def __init__(self,
                 periods: List[int],
                 rules: None | List[str] = None,
                 ) -> None:

        MovingAverageStrategy.__init__(self, periods, rules)
        self.indicator_keys = [f"sma_{period}" for period in self.periods]

    def calculate_indicators(self):
        self.indicator_values = {}
        for i, period in enumerate(self.periods):
            key = self.indicator_keys[i]
            self.indicator_values[key] = calculate_sma(self.data, period)

    @property
    def strategy_name(self):
        return "SMA"

    @property
    def indicator_keys(self):
        return [f"sma_{period}" for period in self.periods]
