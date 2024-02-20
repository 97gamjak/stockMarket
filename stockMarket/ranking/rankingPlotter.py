import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

from scipy.stats import gaussian_kde
from beartype.typing import Tuple, Optional

from .ranking import Ranking
from .rankingFlag import RankingFlag
from .rankingObject import RankingObject


class RankingPlotter:
    def __init__(self, ranking: Ranking):
        self.ranking = ranking

    def plot(self,
             ranking_object: RankingObject,
             filename: Optional[str] = None,
             xlim: Optional[Tuple] = None,
             bins: int = 100
             ):

        self.ranking_object = ranking_object
        self.ranking_object_index = self.ranking.find_index_of_ranking_object(
            self.ranking_object)

        data, _ = self.get_data_correct(xlim)
        no_data = self.get_no_date()
        constraint = self.get_constrained_data()

        total_data = len(self.ranking.contract_scores.values())
        total_displayed_data = len(data) / total_data

        _plt = sns.displot(data, bins=bins, kde=True)

        min_y_value = plt.gca().get_ylim()[0]
        max_y_value = plt.gca().get_ylim()[1]
        min_x_value = plt.gca().get_xlim()[0]
        max_x_value = plt.gca().get_xlim()[1]

        y_range = max_y_value - min_y_value
        x_range = max_x_value - min_x_value

        ax2 = plt.twinx()
        ax2.yaxis.tick_right()
        ax2.yaxis.set_visible(True)
        ax2.yaxis.set_label_position('right')
        ax2.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

        kde = gaussian_kde(data)
        x_values = np.linspace(min(data)-10*x_range,
                               max(data) + 10*x_range, 10000)
        cdf = np.cumsum(kde(x_values)) * \
            (x_values[1] - x_values[0])*total_displayed_data
        ax2.plot(x_values, cdf, color='k')

        for cutoff in self.ranking.ranking_objects[self.ranking_object_index].cutoffs:
            height = np.interp(cutoff, x_values, cdf)

            ax2.hlines(height, min_x_value, max_x_value,
                       colors="r", linestyles="dotted")
            ax2.text(max_x_value - 0.15*x_range, height - 0.01,
                     f'{height:.0%}', va='top', color="r")

            _plt.ax.vlines(cutoff, 0, max_y_value, colors="r")
            _plt.ax.text(cutoff - x_range*0.01, min_y_value-y_range*0.03,
                         f'{cutoff:.1f}', va='center', color="r", rotation=90)

        _plt.ax.set_xlabel(self.ranking_object.description)
        _plt.ax.set_xlim(max(min(data), xlim[0]), min(max(data), xlim[1]))
        ax2.set_ylim(0, 1)
        _plt.ax.legend(
            title=f"N(n.d.): {len(no_data)/total_data:.2%}\nN(c.): {len(constraint)/total_data:.2%}", loc='upper right')

        if filename is not None:
            plt.tight_layout()
            plt.savefig(filename)

    def get_data_correct(self, xlim):
        data = []
        out_of_range_data = []

        for ranking_results in self.ranking.contract_scores.values():
            if ranking_results[self.ranking_object_index].flag == RankingFlag.OK:
                value = ranking_results[self.ranking_object_index].value
                if xlim is None or xlim[0] <= value <= xlim[1]:
                    data.append(value)
                else:
                    out_of_range_data.append(value)

        return data, out_of_range_data

    def get_no_date(self):
        no_data = []
        for ranking_results in self.ranking.contract_scores.values():
            if ranking_results[self.ranking_object_index].flag == RankingFlag.NODATA:
                no_data.append(ranking_results[self.ranking_object_index])

        return no_data

    def get_constrained_data(self):
        constraint = []
        for ranking_results in self.ranking.contract_scores.values():
            if ranking_results[self.ranking_object_index].flag == RankingFlag.CONSTRAINT:
                constraint.append(ranking_results[self.ranking_object_index])

        return constraint
