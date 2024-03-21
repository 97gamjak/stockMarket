import talib

from ._base import Indicator


class RSI(Indicator):
    def __init__(self, data, period, key=None):
        super().__init__(data, key)
        self.indicator = "rsi"
        self.period = period

    def calculate(self):
        self.indicator_values = talib.RSI(self.data, timeperiod=self.period)
        return self.indicator_values


def calculate_rsi(data, period, key=None):
    return RSI(data, period, key).calculate()
