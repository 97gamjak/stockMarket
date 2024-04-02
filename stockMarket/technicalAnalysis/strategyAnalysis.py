import pandas as pd

from .trade import TradeOutcome, TradeStatus


class StrategyAnalysis:
    def __init__(self,
                 trades: pd.DataFrame
                 ) -> None:

        self.trades = trades

    @property
    def average_PL(self) -> float:
        return self.trades[self.trades.trade_status == TradeStatus.CLOSED].PL.mean()

    @property
    def average_R_PL(self) -> float:
        return self.trades[self.trades.trade_status == TradeStatus.CLOSED].R_PL.mean()

    @property
    def win_rate(self) -> float:
        _trades = self.trades[self.trades.trade_status == TradeStatus.CLOSED]
        return len(_trades[_trades.outcome_status == TradeOutcome.WIN]) / len(_trades)

    @property
    def number_of_wins(self) -> int:
        return len(self.trades[self.trades.outcome_status == TradeOutcome.WIN])

    @property
    def number_of_losses(self) -> int:
        return len(self.trades[self.trades.outcome_status == TradeOutcome.LOSS])
