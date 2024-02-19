from __future__ import annotations

import pandas as pd
import numpy as np

from enum import Enum
from beartype.typing import List, Callable

from .contracts import Contracts
from .contract import get_data_from, Contract


class RankingFlag(Enum):
    NONE = "none"
    OK = "ok"
    NODATA = "no data"
    CONSTRAINT = "constraint"


class RankingResult:
    def __init__(self, value=0, score=0, max_score=0, flag=None) -> None:
        self.value = value
        self.score = score
        self.max_score = max_score
        self.flag = flag

        if self.flag is None:
            self.flag = RankingFlag.NONE


class RankingObject:
    def __init__(self, description: str, constraints: List[RankingObject] = None) -> None:
        self.description = description

        if constraints is None:
            self.constraints = []
        else:
            self.constraints = constraints

    def rank(self, contract: Contract = None, date=None, years_back: int = 0):
        result = RankingResult()

        i = 0
        while result.flag == RankingFlag.NONE and i < len(self.constraints):
            result = self.constraints[i].rank(contract, date, years_back)
            i += 1

        return result


class NanRankingConstraint(RankingObject):
    def __init__(self, func):
        super().__init__("NanConstraint")
        self.func = func

    def rank(self, contract: Contract = None, date=None, years_back: int = 0):
        values = self.func(contract)
        value = get_data_from(contract, values, date, years_back)
        if np.isnan(value):
            return RankingResult(value=np.nan, flag=RankingFlag.NODATA)
        else:
            return RankingResult()


class ValueRankingConstraint(RankingObject):
    def __init__(self, func, constraint_func, constraint_value):
        super().__init__("ValueConstraint")
        self.func = func
        self.constraint_func = constraint_func
        self.constraint_value = constraint_value

    def rank(self, contract: Contract = None, date=None, years_back: int = 0):
        values = self.func(contract)
        value = get_data_from(contract, values, date, years_back)
        if not self.constraint_func(value, self.constraint_value):
            return RankingResult(flag=RankingFlag.OK)
        else:
            return RankingResult()

# class ConstraintRankingObject(RankingObject):
#     def __init__(self, description: str, func: Callable, constraints: List[RankingObject] = None) -> None:
#         super().__init__(description, constraints=constraints)
#         self.func = func

#     def rank(self, contract: Contract = None, date=None, years_back: int = 0):
#         result = super().rank()
#         if result.flag != RankingFlag.NONE:
#             return result

#         if self.func(contract):
#             return RankingResult()


class RangeRankingObject(RankingObject):
    def __init__(self, description: str, func: Callable, cutoffs: List[float], scores: List[int], constraints: List[RankingObject] = None) -> None:
        _constraints = [NanRankingConstraint(func)]
        if constraints is not None:
            _constraints += constraints
        super().__init__(description, _constraints)
        self.func = func
        self.cutoffs = cutoffs
        self.scores = scores
        self.max_score = max(scores)

    def rank(self, contract: Contract = None, date=None, years_back: int = 0):
        result = super().rank(contract, date, years_back)
        if result.flag == RankingFlag.OK:
            result.max_score = self.max_score
            return result
        elif result.flag != RankingFlag.NONE:
            return result

        values = self.func(contract)
        value = get_data_from(contract, values, date, years_back)
        cutoff_tuples = list(zip(self.cutoffs[:-1], self.cutoffs[1:]))

        result = RankingResult(flag=RankingFlag.OK)
        result.value = value
        result.max_score = self.max_score
        result.score = self.scores[-1]

        if value < self.cutoffs[0]:
            result.score = self.scores[0]
            return result

        for i, cutoff_tuple in enumerate(cutoff_tuples):
            if cutoff_tuple[0] <= value < cutoff_tuple[1]:
                result.score = self.scores[i+1]
                return result

        return result


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

        contract_scores = {}
        for contract in self.contracts:
            contract_scores[contract.ticker] = []

        for ranking_object in self.ranking_objects:
            ranking_results = []
            for contract in self.contracts:
                try:
                    ranking_result = ranking_object.rank(
                        contract, self.date, self.years_back)
                except Exception as e:
                    ranking_result = RankingResult(
                        flag=RankingFlag.NODATA, value=np.nan)
                ranking_results.append(ranking_result)
                contract_scores[contract.ticker].append(ranking_result)

            self.ranking[ranking_object.description] = [
                ranking_result.value for ranking_result in ranking_results]
            self.ranking[ranking_object.description + " Score"] = [
                ranking_result.score for ranking_result in ranking_results]

        relative_scores = []
        total_scores = []
        nans_constraints = []
        for ticker in self.contracts.tickers:
            total_score = sum(
                [ranking_result.score for ranking_result in contract_scores[ticker]])
            total_max_score = sum(
                [ranking_result.max_score for ranking_result in contract_scores[ticker]])
            try:
                relative_scores.append(f"{total_score/total_max_score:.2%}")
            except ZeroDivisionError:
                relative_scores.append(np.nan)

            total_scores.append(f"{total_score}/{total_max_score}")

            nans = sum([1 for ranking_result in contract_scores[ticker]
                        if ranking_result.flag == RankingFlag.NODATA])

            constraints = sum([1 for ranking_result in contract_scores[ticker]
                               if ranking_result.flag == RankingFlag.CONSTRAINT])

            nans_constraints.append(
                f"{nans}/{constraints}/{len(self.ranking_objects)}")

        self.ranking.insert(2, "Relative Score", relative_scores)
        self.ranking.insert(3, "Absolute Score", total_scores)
        self.ranking.insert(4, "No Data/Constraints/Tot.", nans_constraints)
        self.ranking["sorting"] = self.ranking["Relative Score"].str.replace(
            '%', '').astype(float)
        self.ranking = self.ranking.sort_values(by=["sorting", "Sector", "Name"],
                                                ascending=[False, True, True]).drop(columns=["sorting"])
