import datetime as dt

from beartype.typing import List
from tqdm import tqdm

from .indicators import calculate_ema, candle_body_outside_range
from ._strategy import StrategyBase
from .technicals import Technicals
from stockMarket.utils import Period


class Strategy(StrategyBase):
    def __init__(self, tickers: List[str] | str):
        super().__init__(tickers)

        self.result_logger = {}
        self.meta_data_logger = {}
        self.error_logger = {}

    def screen(self,
               candle_period: str | Period | None = None,
               start=None,
               end=None,
               ) -> None:

        super().screen(candle_period, start, end)

        logger_file = open("result_logger.txt", "w")
        meta_file = open("meta_data_logger.txt", "w")
        error_file = open("error_logger.txt", "w")

        #fmt: off
        if end is None:
            end = dt.datetime.now().date()

        logger_file.write(f"Screening for weekly candles from {start} to {end}\n\n\n")
        #fmt: on

        for ticker in tqdm(self.tickers):
            contract = Technicals(ticker=ticker)
            contract.init_pricing_data(
                self.candle_period, n_bars=self.n_bars)

            pricing_data = contract.pricing_data
            self.result_logger[ticker] = {}
            self.meta_data_logger[ticker] = {}

            try:
                self.ema_8 = calculate_ema(pricing_data, 8)
                self.ema_20 = calculate_ema(pricing_data, 20)
                self.ema_50 = calculate_ema(pricing_data, 50)
            except Exception as e:
                self.error_logger[ticker] = e
                continue

            for index in range(self.start_index, self.end_index + 1):
                if index > len(pricing_data):
                    break

                index = -index
                self._strategy(pricing_data, ticker, index)

            if self.result_logger[ticker] != {}:

                logger_file.write(f"Ticker: {ticker}\n")
                for key, value in self.result_logger[ticker].items():
                    logger_file.write(f"{key}: {value}\n")
                logger_file.write("\n")
                logger_file.flush()

                meta_file.write(f"Ticker: {ticker}\n")
                for key, value in self.meta_data_logger[ticker].items():
                    meta_file.write(f"{key}\n")
                    meta_file.write(value)
                meta_file.write("\n")
                meta_file.flush()

            if ticker in self.error_logger:
                error_file.write(f"Ticker: {ticker}\n")
                error_file.write(f"{self.error_logger[ticker]}\n")
                error_file.write("\n")
                error_file.flush()

        logger_file.close()
        meta_file.close()

    def _strategy(self, data, ticker, index):
        self._indicator(data, index)
        self._rules(data, ticker, index)

    def _indicator(self, data, index):
        self.fib_bools, self.fib_data = candle_body_outside_range(data.iloc[index], [
                                                                  0.3, 0.7])

    def _rules(self, data, ticker, index):
        candle = data.iloc[index]
        ema_8 = self.ema_8.iloc[index]
        ema_20 = self.ema_20.iloc[index]
        ema_50 = self.ema_50.iloc[index]

        if self.fib_bools[1]:
            if ema_8 > ema_20 > ema_50:
                if candle.low <= ema_8:
                    self.result_logger[ticker][candle.name] = 'BULLISH'
                    #fmt: off
                    message  = f"\tema_8   : {ema_8:8.2f}, ema_20   : {ema_20:8.2f}, ema_50  : {ema_50:8.2f}\n"
                    message += f"\tema_8-20: {ema_8/ema_20:8.2f}, ema_20-50: {ema_20 /ema_50:8.2f}, ema_8-50: {ema_8/ema_50:8.2f}\n"
                    #fmt: on
                    self.meta_data_logger[ticker][candle.name] = message

        # if self.fib_bools[0]:
        #     if ema_8 < ema_20 < ema_50:
        #         if candle.high >= ema_8:
        #             self.result_logger[ticker][candle.name] = 'SELL'
        #             self.meta_data_logger[ticker][candle.name] = f"ema_8: {ema_8}, ema_20: {
        #                 ema_20}, ema_50: {ema_50}"
