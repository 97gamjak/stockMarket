import numpy as np
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

from ..ranking import Ranking
from stockMarket.core.pricing import Pricing
from stockMarket.utils.period import Period


class BackTester:
    list_benchmarks = ["SPX", "SPXEW", "MXWO"]
    colors = ['r', 'g', 'c', 'm', 'y', 'k']

    def __init__(self, contracts, ranking_objects):
        self.contracts = contracts
        self.ranking_objects = ranking_objects

    def back_test(self, date=None, years_back=1, period="annual"):

        self.ranking = Ranking(
            self.contracts, self.ranking_objects, date=date, years_back=years_back)
        self.ranking.rank()

        self.get_performance()
        # self.get_performance(date, years_back, period)

        data = [
            data for data in self.performances.values() if not np.isnan(data[0]) and not np.isnan(data[1])]

        weights = self.ranking.ranking["Relative Score"]
        weights = [float(weight.replace("%", "")) / 100 for weight in weights]
        weights = [weight for i, weight in enumerate(
            weights) if not np.isnan(list(self.performances.values())[i][0]) and not np.isnan(list(self.performances.values())[i][1])]

        weights = np.array(weights)

        ew_total_performance = self.equal_weighted_performance(data)
        weighted_total_performance = self.weighted_performance(data, weights)
        self.calculate_benchmarks(self.list_benchmarks)

        plt.plot(ew_total_performance)
        plt.plot(weighted_total_performance)

        for i, benchmark in enumerate(self.benchmarks):
            plt.hlines(self.benchmarks[benchmark], 0, len(
                data), label=benchmark, color=self.colors[i])

        plt.plot(weighted_total_performance - ew_total_performance)

        plt.xlim(0, 100)
        ax = plt.gca()
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
        plt.legend()
        plt.show()

    def get_performance(self):
        self.performances = {}
        for ticker in self.ranking.ranking.index:
            try:
                old_performance = self.contracts[ticker].get_price_by_date(
                    years_back=1)
                new_performance = self.contracts[ticker].get_price_by_date(
                    years_back=0)
                self.performances[ticker] = (new_performance, old_performance)
            except Exception:
                self.performances[ticker] = (np.nan, np.nan)

    def calculate_ranking_dates(self, date, years_back, period):
        if date is None:
            date = dt.date.today()
        self.date = date - pd.DateOffset(years=years_back)
        self.date = pd.to_datetime(self.date).date()

        self.period = Period(period)
        self.dates = self.period.calculate_dates(self.date, dt.date().today())
        print(self.dates)

    def perform_ranking(self, date, years_back):
        ranking = Ranking(self.contracts, self.ranking_objects,
                          date=date, years_back=years_back)
        return ranking.rank()

    def equal_weighted_performance(self, data):
        new_performance = np.array([data[0] for data in data])
        old_performance = np.array([data[1] for data in data])
        performance = (new_performance - old_performance) / old_performance
        total_performance = np.cumsum(performance) / \
            np.cumsum(np.ones(len(performance)))
        return total_performance

    def weighted_performance(self, data, weights):
        new_performance = np.array([data[0] for data in data])
        old_performance = np.array([data[1] for data in data])
        performance = (new_performance - old_performance) / old_performance
        total_performance = np.cumsum(performance*weights) / \
            np.cumsum(weights)
        return total_performance

    def calculate_benchmarks(self, list_benchmarks):
        self.benchmarks = {}
        for benchmark in list_benchmarks:
            try:
                pricing = Pricing(ticker=benchmark)
                pricing.update_prices(n_bars=500)
                price_data = pricing.get_pricing_data()
                date = dt.date.today() - pd.DateOffset(years=1)
                date = pd.to_datetime(date).date()
                new_performance = price_data.iloc[-1].close
                old_performance = price_data[:date].iloc[-1].close
                self.benchmarks[benchmark] = (
                    new_performance - old_performance) / old_performance
            except Exception:
                self.benchmarks[benchmark] = np.nan
        return self.benchmarks
