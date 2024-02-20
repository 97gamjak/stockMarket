import numpy as np
import matplotlib.pyplot as plt

from ..ranking import Ranking


class BackTester:
    def __init__(self, contracts, ranking_list):
        self.contracts = contracts
        self.ranking_list = ranking_list

    def back_test(self):
        self.ranking = Ranking(self.contracts, self.ranking_list, years_back=1)
        self.ranking.rank()

        self.get_performance()

        data = [
            data for data in self.performances.values() if not np.isnan(data)]

        cumulative_sum = np.cumsum(data)

        plt.plot(cumulative_sum)
        plt.show()

    def get_performance(self):
        self.performances = {}
        for ticker in self.ranking.ranking.index:
            try:
                old_performance = self.contracts[ticker].get_price_by_date(
                    years_back=1)
                new_performance = self.contracts[ticker].get_price_by_date(
                    years_back=0)
                self.performances[ticker] = (
                    new_performance - old_performance) / old_performance
            except:
                self.performances[ticker] = np.nan
