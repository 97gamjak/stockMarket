import pandas as pd

from beartype.typing import Optional

from ._meta import MetaDecorator
from ._pipe import (
    filter_date_range,
    filter_closed_trades,
    filter_wins,
    filter_losses,
    filter_date_range,
)


class StrategyAnalysis(metaclass=MetaDecorator):
    def __init__(self,
                 trades: pd.DataFrame
                 ) -> None:

        self.trades = trades
        self._start_date = None
        self._end_date = None

    def average_PL(self,
                   start_date: Optional[pd.Timestamp] = None,
                   end_date: Optional[pd.Timestamp] = None,
                   ) -> float:

        return (self.trades.pipe(filter_date_range, start_date, end_date)
                           .pipe(filter_closed_trades)
                           .PL.mean())

    def average_R_PL(self,
                     start_date: Optional[pd.Timestamp] = None,
                     end_date: Optional[pd.Timestamp] = None,
                     ) -> float:

        return (self.trades.pipe(filter_date_range, start_date, end_date)
                           .pipe(filter_closed_trades)
                           .R_PL.mean())

    def win_loss_ratio(self,
                       start_date: Optional[pd.Timestamp] = None,
                       end_date: Optional[pd.Timestamp] = None,
                       ) -> Optional[float]:

        number_of_wins = self.number_of_wins(start_date, end_date)
        number_of_losses = self.number_of_losses(start_date, end_date)

        if number_of_losses == 0:
            return None
        else:
            return number_of_wins / number_of_losses

    def probability_of_win(self,
                           start_date: Optional[pd.Timestamp] = None,
                           end_date: Optional[pd.Timestamp] = None,
                           ) -> Optional[float]:

        trades = (self.trades.pipe(filter_date_range, start_date, end_date)
                             .pipe(filter_closed_trades))

        if len(trades) == 0:
            return None
        else:
            return len(trades.pipe(filter_wins)) / len(trades)

    def number_of_wins(self,
                       start_date: Optional[pd.Timestamp] = None,
                       end_date: Optional[pd.Timestamp] = None,
                       ) -> int:

        return len(self.trades.pipe(filter_date_range, start_date, end_date)
                              .pipe(filter_closed_trades)
                              .pipe(filter_wins))

    def number_of_losses(self,
                         start_date: Optional[pd.Timestamp] = None,
                         end_date: Optional[pd.Timestamp] = None,
                         ) -> int:

        return len(self.trades.pipe(filter_date_range, start_date, end_date)
                              .pipe(filter_closed_trades)
                              .pipe(filter_losses))

    def predicted_outcome(self,
                          start_date: Optional[pd.Timestamp] = None,
                          end_date: Optional[pd.Timestamp] = None,
                          ):

        return (self.trades.pipe(filter_date_range, start_date, end_date)
                           .pipe(filter_closed_trades)
                           .PRED_OUTCOME)

    def outcome(self,
                start_date: Optional[pd.Timestamp] = None,
                end_date: Optional[pd.Timestamp] = None,
                ):

        return (self.trades.pipe(filter_date_range, start_date, end_date)
                           .pipe(filter_closed_trades)
                           .OUTCOME)

    @property
    def start_date(self) -> Optional[pd.Timestamp]:
        return self._start_date

    @start_date.setter
    def start_date(self, value: Optional[pd.Timestamp]) -> None:
        self._start_date = value

    @property
    def end_date(self) -> Optional[pd.Timestamp]:
        return self._end_date

    @end_date.setter
    def end_date(self, value: Optional[pd.Timestamp]) -> None:
        self._end_date = value
