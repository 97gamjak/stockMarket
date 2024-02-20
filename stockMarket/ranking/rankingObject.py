from __future__ import annotations

import numpy as np

from beartype.typing import List, Callable

from .rankingResult import RankingResult
from .rankingFlag import RankingFlag
from stockMarket.core import Contract
from stockMarket.core.contract import get_data_from


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
            return RankingResult(flag=RankingFlag.CONSTRAINT)
        else:
            return RankingResult()


class RangeRankingObject(RankingObject):
    def __init__(self, description: str, func: Callable, cutoffs: List[float], scores: List[int], constraints: List[RankingObject] = None) -> None:
        _constraints = [NanRankingConstraint(func)]
        if constraints is not None:
            _constraints += constraints
        super().__init__(description, _constraints)

        assert len(cutoffs) == len(scores) - 1

        self.func = func
        self.cutoffs = cutoffs
        self.scores = scores
        self.max_score = max(scores)

    def rank(self, contract: Contract = None, date=None, years_back: int = 0):
        result = super().rank(contract, date, years_back)
        if result.flag == RankingFlag.NODATA:
            return result

        values = self.func(contract)
        value = get_data_from(contract, values, date, years_back)

        if result.flag != RankingFlag.NONE:
            result.value = value
            result.max_score = self.max_score
            return result

        cutoff_tuples = list(zip(self.cutoffs[:-1], self.cutoffs[1:]))

        result = RankingResult(flag=RankingFlag.OK)
        result.value = value
        result.max_score = self.max_score
        result.score = self.scores[-1]

        if value < self.cutoffs[0]:
            result.score = self.scores[0]
        elif value < self.cutoffs[-1]:
            for i, cutoff_tuple in enumerate(cutoff_tuples):
                if cutoff_tuple[0] <= value < cutoff_tuple[1]:
                    result.score = self.scores[i+1]

        result.score = result.score / result.max_score
        return result
