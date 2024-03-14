import talib
import numpy as np
import pandas as pd

from abc import abstractmethod
from beartype.typing import List

from stockMarket.utils import caching


class Indicator:
    def __init__(self, candle_data, key=None):

        if key is None and not isinstance(candle_data, pd.DataFrame):
            self.candle_data = None
            self.data = candle_data
        elif key is None:
            self.candle_data = candle_data
            self.data = candle_data["close"]
        else:
            self.candle_data = candle_data
            self.data = candle_data[key]

        self.indicator = None
        self.indicator_values = None

    @abstractmethod
    def calculate(self):
        pass


class EMA(Indicator):
    def __init__(self, data, period, key=None):
        super().__init__(data, key)
        self.indicator = "ema"
        self.period = period

    def calculate(self):
        self.indicator_values = talib.EMA(self.data, timeperiod=self.period)
        return self.indicator_values


def calculate_ema(data, period, key=None, cache=None):
    if cache is not None:
        return cache
    else:
        return EMA(data, period, key).calculate()


class FIB(Indicator):
    def __init__(self, candle_data, percentages: List):
        super().__init__(candle_data)
        self.indicator = "fib"
        self.percentages = np.array(percentages)
        self.high = candle_data.high
        self.low = candle_data.low
        self.open = candle_data.open
        self.close = candle_data.close

    def calculate(self):
        candle_range = self.high - self.low
        self.indicator_values = sorted(
            candle_range * self.percentages + self.low)

        return self.indicator_values

    def candle_body_outside_range(self):
        if len(self.percentages) != 2:
            raise ValueError(
                "Fibonacci retracement to check if candle body is outside range only works for 2 percentages")

        self.calculate()

        body_below_low_fib = self.open < self.indicator_values[
            0] and self.close < self.indicator_values[0]
        body_above_high_fib = self.open > self.indicator_values[
            1] and self.close > self.indicator_values[1]

        return (body_below_low_fib, body_above_high_fib)


def calculate_fib(data, percentages):
    return FIB(data, percentages).calculate()


def candle_body_outside_range(data, percentages):
    fib = FIB(data, percentages)
    boolean_check = fib.candle_body_outside_range()
    return boolean_check, fib.indicator_values
