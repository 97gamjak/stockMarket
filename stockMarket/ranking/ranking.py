from __future__ import annotations

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns

from scipy.stats import gaussian_kde
from beartype.typing import List

from .rankingFlag import RankingFlag
from .rankingResult import RankingResult
from .rankingObject import RankingObject
from stockMarket.core import Contracts


class Ranking:
    def __init__(self, contracts: Contracts, ranking_objects: List[RankingObject], date=None, years_back=0) -> None:
        self.date = date
        self.years_back = years_back
        self.contracts = contracts
        self.ranking_objects = ranking_objects

    def rank(self):
        self.ranking = pd.DataFrame(
            index=self.contracts.tickers, columns=["Name", "Sector"])

        self.ranking["Name"] = self.contracts.long_names
        self.ranking["Sector"] = self.contracts.sectors

        self.contract_scores = {}
        for contract in self.contracts:
            self.contract_scores[contract.ticker] = []

        for ranking_object in self.ranking_objects:
            ranking_results = []
            for contract in self.contracts:
                try:
                    ranking_result = ranking_object.rank(
                        contract, self.date, self.years_back)
                except Exception:
                    ranking_result = RankingResult(
                        flag=RankingFlag.NODATA, value=np.nan)
                ranking_results.append(ranking_result)
                self.contract_scores[contract.ticker].append(ranking_result)

            self.ranking[ranking_object.description] = [
                ranking_result.value for ranking_result in ranking_results]
            self.ranking[ranking_object.description + " Score"] = [
                ranking_result.score for ranking_result in ranking_results]

        relative_scores = []
        total_scores = []
        no_data_constraints = []
        for ticker in self.contracts.tickers:
            total_score = sum(
                [ranking_result.score for ranking_result in self.contract_scores[ticker]])
            total_max_score = sum(
                [1 if ranking_result.max_score > 0 else 0 for ranking_result in self.contract_scores[ticker]])
            try:
                relative_scores.append(f"{total_score/total_max_score:.2%}")
            except ZeroDivisionError:
                relative_scores.append("0.00%")

            total_scores.append(f"{total_score}/{total_max_score}")

            no_data = sum([1 for ranking_result in self.contract_scores[ticker]
                           if ranking_result.flag == RankingFlag.NODATA])

            constraints = sum([1 for ranking_result in self.contract_scores[ticker]
                               if ranking_result.flag == RankingFlag.CONSTRAINT])

            no_data_constraints.append(
                f"{no_data}*{constraints}*{len(self.ranking_objects)}")

        self.ranking.insert(2, "Relative Score", relative_scores)
        self.ranking.insert(3, "Absolute Score", total_scores)
        self.ranking.insert(4, "No Data/Constraints/Tot.", no_data_constraints)
        self.ranking["sorting"] = self.ranking["Relative Score"].str.replace(
            '%', '').astype(float)
        self.ranking = self.ranking.sort_values(by=["sorting", "Sector", "Name"],
                                                ascending=[False, True, True]).drop(columns=["sorting"])

    def find_index_of_ranking_object(self, ranking_object: RankingObject):
        for i, _ranking_object in enumerate(self.ranking_objects):
            if _ranking_object.description == ranking_object.description:
                return i

        raise ValueError(
            f"Ranking object {ranking_object.description} not found")
