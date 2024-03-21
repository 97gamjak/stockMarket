import talib

from abc import ABCMeta, abstractmethod

from ._base import Indicator


class MovingAverage(Indicator, metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, data, period, key=None):
        super().__init__(data, key)
        self.period = period


class EMA(MovingAverage):
    def __init__(self, data, period, key=None):
        MovingAverage.__init__(self, data, period, key)
        self.indicator = "ema"

    def calculate(self):
        self.indicator_values = talib.EMA(self.data, timeperiod=self.period)
        return self.indicator_values


def calculate_ema(data, period, key=None):
    return EMA(data, period, key).calculate()


class SMA(MovingAverage):
    def __init__(self, data, period, key=None):
        MovingAverage.__init__(self, data, period, key)
        self.indicator = "sma"

    def calculate(self):
        self.indicator_values = talib.SMA(self.data, timeperiod=self.period)
        return self.indicator_values


def calculate_sma(data, period, key=None):
    return SMA(data, period, key).calculate()
