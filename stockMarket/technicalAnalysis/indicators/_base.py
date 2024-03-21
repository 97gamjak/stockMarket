import pandas as pd

from abc import ABCMeta, abstractmethod


class Indicator(metaclass=ABCMeta):
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
