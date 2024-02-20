from .rankingFlag import RankingFlag


class RankingResult:
    def __init__(self, value=0, score=0, max_score=0, flag=None) -> None:
        self.value = value
        self.score = score
        self.max_score = max_score
        self.flag = flag

        if self.flag is None:
            self.flag = RankingFlag.NONE
