import pandas as pd

from beartype.typing import List, Callable, Tuple

from .contracts import Contracts


class RankingObject:
    def __init__(self, func: Callable, description: str) -> None:
        self.func = func
        self.description = description


class RangeRankingObject(RankingObject):
    score = 0

    def __init__(self, func: Callable, description: str, range: List[Tuple]):
        def inner_func(contract):
            value = func(contract)
            for min_value, max_value, score in range:
                if min_value is None and max_value is None:
                    return value, self.score
                elif min_value is None:
                    if value <= max_value:
                        return value, score
                    else:
                        continue

                elif max_value is None:
                    if value >= min_value:
                        return value, score
                    else:
                        continue

                elif min_value <= value <= max_value:
                    return value, score

            return value, 0

        super().__init__(inner_func, description)


class Ranking:
    def __init__(self, contracts: Contracts, ranking_objects: List[RankingObject]) -> None:
        self.contracts = contracts
        self.ranking_objects = ranking_objects

    def rank(self):
        self.ranking = pd.DataFrame(
            index=self.contracts.tickers, columns=["Name", "Sector"])

        self.ranking["Name"] = self.contracts.long_names
        self.ranking["Sector"] = self.contracts.sectors

        contract_scores = {}
        for contract in self.contracts:
            contract_scores[contract.ticker] = 0

        for ranking_object in self.ranking_objects:
            scores = []
            values = []
            for contract in self.contracts:
                value, score = ranking_object.func(contract)
                values.append(value)
                scores.append(score)
                contract_scores[contract.ticker] += score

            self.ranking[ranking_object.description] = values
            self.ranking[ranking_object.description + " Score"] = scores

        self.ranking.insert(2, "Total Score", list(contract_scores.values()))
        self.ranking.sort_values(
            by=["Total Score", "Sector", "Name"], ascending=[False, True, True], inplace=True)
