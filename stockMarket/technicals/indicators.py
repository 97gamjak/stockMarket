import talib
import numpy as np

from abc import abstractmethod
from beartype.typing import List


class Indicator:
    def __init__(self, data):
        self.data = data
        self.indicator = None
        self.indicator_values = None

    @abstractmethod
    def calculate(self):
        pass


class EMA(Indicator):
    def __init__(self, data, period):
        super().__init__(data)
        self.indicator = "ema"
        self.period = period

    def calculate(self):
        self.indicator_values = talib.EMA(self.data, timeperiod=self.period)
        return self.indicator_values


class FIB(Indicator):
    def __init__(self, data, percentages: List):
        super().__init__(data)
        self.indicator = "fib"
        self.percentages = np.array(percentages)

    def calculate(self):
        candle_range = data.high - data.low
        self.indicator_values = candle_range * self.percentages + candle.low

        return self.indicator_values
