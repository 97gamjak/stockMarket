import numpy as np
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

from tqdm import tqdm

from ..ranking import Ranking
from stockMarket.core.pricing import Pricing
from stockMarket.utils.period import Period


class BackTester:
    list_benchmarks = ["SPX", "SPXEW", "MXWO", "NDX"]
    colors = ['r', 'g', 'c', 'm', 'y', 'k']

    def __init__(self, contracts, ranking_objects):
        self.contracts = contracts
        self.ranking_objects = ranking_objects
        self.plotting_title = "Back Test\n"

    def back_test(self, date=None, end_date=None, years_back=1, period="annual", frequency="annual"):

        self.dates, self.performance_dates = self.calculate_ranking_dates(
            date, end_date, years_back, period, frequency)

        old_price_matrix = np.matrix(
            np.zeros((len(self.dates), len(self.contracts))))
        new_price_matrix = np.matrix(
            np.zeros((len(self.dates), len(self.contracts))))
        weights_matrix = np.matrix(
            np.zeros((len(self.dates), len(self.contracts))))
        for i, date in enumerate(tqdm(self.dates)):
            self.ranking = self.perform_ranking(date)
            self.prices = self.get_pricing_data(
                date, self.performance_dates[i])
            weights = self.get_weights()
            old_price_matrix[self.dates.index(date)] = [price[1]
                                                        for price in self.prices.values()]
            new_price_matrix[self.dates.index(date)] = [price[0]
                                                        for price in self.prices.values()]
            weights_matrix[self.dates.index(date)] = weights

        self.average_performance = self.calculate_performance(
            old_price_matrix, new_price_matrix)
        self.ew_total_performance = self.equal_weighted_performance(
            self.average_performance)
        self.weighted_total_performance = self.weighted_performance(
            old_price_matrix, new_price_matrix, weights_matrix)

        self.benchmarks = self.calculate_benchmarks(self.list_benchmarks)

    def calculate_ranking_dates(self, date, end_date, years_back, period, frequency):
        if date is None:
            date = dt.date.today()
        date = date - pd.DateOffset(years=years_back)
        date = pd.to_datetime(date).date()

        period = Period(period)
        frequency = Period(frequency)

        if end_date is None:
            end_date = dt.date.today()

        dates = []
        while date + period.period_time <= end_date:
            dates.append(date)
            date += frequency.period_time

        performance_dates = [date + period.period_time for date in dates]

        self.plotting_title += f"{dates[0]} - {performance_dates[-1]}\n"
        self.plotting_title += f"Period: {period.period_string} * {period.amount}\n"
        self.plotting_title += f"Frequency: {frequency.period_string} * {frequency.amount}\n"
        self.plotting_title += f"Average over {len(dates)} periods\n"

        return dates, performance_dates

    def perform_ranking(self, date):
        ranking = Ranking(self.contracts, self.ranking_objects, date=date)
        ranking.rank()
        return ranking

    def get_pricing_data(self, date, performance_date):
        prices = {}
        for ticker in self.ranking.ranking.index:
            try:
                old_price = self.contracts[ticker].get_price_by_date(date=date)
                new_price = self.contracts[ticker].get_price_by_date(
                    date=performance_date)
                prices[ticker] = (new_price, old_price)
            except Exception:
                prices[ticker] = (np.nan, np.nan)

        return prices

    def get_weights(self):
        weights = self.ranking.ranking["Relative Score"]
        weights = [float(weight.replace("%", "")) / 100 for weight in weights]
        weights = np.array(weights)

        return weights

    def calculate_performance(self, old_price_matrix, new_price_matrix):
        n_contracts = len(self.contracts)
        n_dates = len(self.dates)
        performance = np.matrix(np.zeros((n_dates, n_contracts)))

        for i in range(n_dates):
            for j in range(n_contracts):
                if np.isnan(old_price_matrix[i, j]) or np.isnan(new_price_matrix[i, j]):
                    performance[i, j] = np.nan
                else:
                    performance[i, j] = (
                        new_price_matrix[i, j] - old_price_matrix[i, j]) / old_price_matrix[i, j]

        average_performance = np.array(np.nanmean(performance, axis=0))[0]

        average_performance = average_performance[~np.isnan(
            average_performance)]

        return average_performance

    def equal_weighted_performance(self, average_performance):

        total_performance = np.cumsum(average_performance) / \
            np.cumsum(np.ones(len(average_performance)))

        return total_performance

    def weighted_performance(self, old_price_matrix, new_price_matrix, weights):
        n_contracts = len(self.contracts)
        n_dates = len(self.dates)
        performance = np.matrix(np.zeros((n_dates, n_contracts)))

        for i in range(n_dates):
            for j in range(n_contracts):
                if np.isnan(old_price_matrix[i, j]) or np.isnan(new_price_matrix[i, j]):
                    performance[i, j] = np.nan
                else:
                    performance[i, j] = (
                        new_price_matrix[i, j] - old_price_matrix[i, j]) / old_price_matrix[i, j] * weights[i, j]

        average_weights = np.array(np.nanmean(weights, axis=0))[0]
        average_performance = np.array(np.nanmean(performance, axis=0))[0]

        average_weights = average_weights[~np.isnan(average_performance)]
        average_performance = average_performance[~np.isnan(
            average_performance)]

        total_performance = np.cumsum(average_performance) / \
            np.cumsum(average_weights)

        return total_performance

    def calculate_benchmarks(self, list_benchmarks):
        benchmarks = {}
        for benchmark in list_benchmarks:
            performances = []
            for i, date in enumerate(self.dates):
                try:
                    pricing = Pricing(ticker=benchmark)
                    pricing.update_prices(n_bars=5000)
                    price_data = pricing.get_pricing_data()
                    new_performance = price_data[:self.performance_dates[i]
                                                 ].iloc[-1].close
                    old_performance = price_data[:date].iloc[-1].close
                    performances.append(
                        (new_performance - old_performance) / old_performance)
                except Exception:
                    performances.append(np.nan)

            benchmarks[benchmark] = np.nanmean(performances)
        return benchmarks

    def plot_cumulative_performance(self, filename=None):
        fig, ax = plt.subplots(1, 2, figsize=(20, 10))
        ax[0].plot(self.ew_total_performance, label="EW")
        ax[0].plot(self.weighted_total_performance, label="Weighted")

        for i, benchmark in enumerate(self.benchmarks):
            ax[0].hlines(self.benchmarks[benchmark], 0, len(
                self.contracts), label=benchmark, color=self.colors[i])

        ax[1].plot(self.weighted_total_performance - self.ew_total_performance)

        ax[0].yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
        ax[1].yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
        ax[0].legend()
        ax[0].set_ylabel("Performance")
        ax[1].set_ylabel("Performance Difference Weighted - EW")

        fig.suptitle(self.plotting_title)

        if filename is not None:
            plt.tight_layout()
            plt.savefig(filename)
        else:
            plt.show()

    def plot_single_performances(self, filename=None):
        n = int(len(self.average_performance)/5.0)
        running_average = np.convolve(self.average_performance, np.ones(
            n) / n, mode='valid')

        # plt.plot(self.average_performance)
        plt.plot(running_average, label=f"Running Average over {n} contracts")

        ax = plt.gca()
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

        for i, benchmark in enumerate(self.benchmarks):
            plt.hlines(self.benchmarks[benchmark], 0, len(
                self.contracts), label=benchmark, color=self.colors[i])

        plt.legend()
        plt.title(self.plotting_title)

        if filename is not None:
            plt.tight_layout()
            plt.savefig(filename)
        else:
            plt.show()
