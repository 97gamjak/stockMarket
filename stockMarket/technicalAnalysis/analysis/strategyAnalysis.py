import pandas as pd

from decorator import decorator
from beartype.typing import Optional

from ._pipe import (
    filter_date_range,
    filter_closed_trades,
    filter_wins,
    filter_losses,
    filter_open_on_day,
    filter_trade_executed,
)


class StrategyAnalysis:
    def __init__(self,
                 trades: pd.DataFrame
                 ) -> None:

        self.trades = trades

    def win_loss_ratio(self,
                       start_date: Optional[pd.Timestamp] = None,
                       end_date: Optional[pd.Timestamp] = None,
                       ) -> Optional[float]:

        number_of_wins = self.number_of_wins(
            start_date=start_date,
            end_date=end_date
        )
        number_of_losses = self.number_of_losses(
            start_date=start_date,
            end_date=end_date
        )

        if number_of_losses == 0:
            return None
        else:
            return number_of_wins / number_of_losses

    def probability_of_win(self,
                           start_date: Optional[pd.Timestamp] = None,
                           end_date: Optional[pd.Timestamp] = None,
                           ) -> Optional[float]:

        trades = (self.trades.pipe(filter_date_range, start_date=start_date, end_date=end_date)
                             .pipe(filter_closed_trades))

        if len(trades) == 0:
            return None
        else:
            return len(trades.pipe(filter_wins)) / len(trades)

    def number_of_wins(self,
                       start_date: Optional[pd.Timestamp] = None,
                       end_date: Optional[pd.Timestamp] = None,
                       ) -> int:

        return len(self.trades.pipe(filter_date_range, start_date=start_date, end_date=end_date)
                              .pipe(filter_closed_trades)
                              .pipe(filter_wins))

    def number_of_losses(self,
                         start_date: Optional[pd.Timestamp] = None,
                         end_date: Optional[pd.Timestamp] = None,
                         ) -> int:

        return len(self.trades.pipe(filter_date_range, start_date=start_date, end_date=end_date)
                              .pipe(filter_closed_trades)
                              .pipe(filter_losses))

    def predicted_outcome(self,
                          start_date: Optional[pd.Timestamp] = None,
                          end_date: Optional[pd.Timestamp] = None,
                          ):

        return (self.trades.pipe(filter_date_range, start_date=start_date, end_date=end_date)
                           .pipe(filter_closed_trades)
                           .PRED_OUTCOME)

    def win_outcome(self,
                    start_date: Optional[pd.Timestamp] = None,
                    end_date: Optional[pd.Timestamp] = None,
                    ):

        return (self.trades.pipe(filter_date_range, start_date=start_date, end_date=end_date)
                           .pipe(filter_closed_trades)
                           .pipe(filter_wins)
                           .OUTCOME)

    def loss_outcome(self,
                     start_date: Optional[pd.Timestamp] = None,
                     end_date: Optional[pd.Timestamp] = None,
                     ):

        return (self.trades.pipe(filter_date_range, start_date=start_date, end_date=end_date)
                           .pipe(filter_closed_trades)
                           .pipe(filter_losses)
                           .OUTCOME)

    def outcome(self,
                start_date: Optional[pd.Timestamp] = None,
                end_date: Optional[pd.Timestamp] = None,
                ):

        return (self.trades.pipe(filter_date_range, start_date=start_date, end_date=end_date)
                           .pipe(filter_closed_trades)
                           .OUTCOME)

    def required_capital(self,
                         start_date: Optional[pd.Timestamp] = None,
                         end_date: Optional[pd.Timestamp] = None,
                         ):

        return (self.trades.pipe(filter_date_range, start_date=start_date, end_date=end_date)
                           .pipe(filter_closed_trades)
                           .REQ_CAPITAL)

    def investment(self,
                   start_date: Optional[pd.Timestamp] = None,
                   end_date: Optional[pd.Timestamp] = None,
                   ):

        return (self.trades.pipe(filter_date_range, start_date=start_date, end_date=end_date)
                           .pipe(filter_closed_trades)
                           .INVESTMENT)

    def total_days(self,
                   start_date: Optional[pd.Timestamp] = None,
                   end_date: Optional[pd.Timestamp] = None,
                   ):

        return (self.trades.pipe(filter_date_range, start_date=start_date, end_date=end_date)
                           .pipe(filter_closed_trades)
                           .TOTAL_DAYS)

    def PL(self,
           start_date: Optional[pd.Timestamp] = None,
           end_date: Optional[pd.Timestamp] = None,
           ):

        return (self.trades.pipe(filter_date_range, start_date=start_date, end_date=end_date)
                           .pipe(filter_closed_trades)
                           .PL)

    def R_PL(self,
             start_date: Optional[pd.Timestamp] = None,
             end_date: Optional[pd.Timestamp] = None,
             ):

        return (self.trades.pipe(filter_date_range, start_date=start_date, end_date=end_date)
                           .pipe(filter_closed_trades)
                           .R_PL)

    def positive_expectancy(self,
                            start_date: Optional[pd.Timestamp] = None,
                            end_date: Optional[pd.Timestamp] = None,
                            ) -> Optional[float]:

        PL = self.PL(start_date=start_date, end_date=end_date).mean()
        probability_of_win = self.probability_of_win(
            start_date=start_date,
            end_date=end_date
        )

        return self._positive_expectancy(PL, probability_of_win)

    def R_positive_expectancy(self,
                              start_date: Optional[pd.Timestamp] = None,
                              end_date: Optional[pd.Timestamp] = None,
                              ) -> Optional[float]:

        R_PL = self.R_PL(start_date=start_date, end_date=end_date).mean()
        probability_of_win = self.probability_of_win(
            start_date=start_date,
            end_date=end_date
        )

        return self._positive_expectancy(R_PL, probability_of_win)

    def _positive_expectancy(self,
                             PL: float,
                             probability_of_win: float,
                             ) -> Optional[float]:

        return (1 + PL)*probability_of_win - 1

    def predicted_yield(self,
                        start_date: Optional[pd.Timestamp],
                        end_date: Optional[pd.Timestamp],
                        ) -> Optional[float]:

        return self._yield("PRED_OUTCOME", start_date=start_date, end_date=end_date)

    def real_yield(self,
                   start_date: Optional[pd.Timestamp],
                   end_date: Optional[pd.Timestamp],
                   ) -> Optional[float]:

        return self._yield("OUTCOME", start_date=start_date, end_date=end_date)

    def _yield(self,
               key: "str",
               start_date: Optional[pd.Timestamp],
               end_date: Optional[pd.Timestamp],
               ) -> Optional[float]:

        outcome = (self.trades.pipe(filter_date_range, start_date=start_date, end_date=end_date)
                              .pipe(filter_closed_trades)[key]
                   ).sum()

        max_investment = self.max_daily_investment(start_date, end_date)

        return outcome / max_investment * 365 / (end_date - start_date).days

    def max_daily_investment(self,
                             start_date: pd.Timestamp,
                             end_date: pd.Timestamp,
                             ) -> Optional[float]:

        return max(
            self._date_investment_dictionary(
                start_date,
                end_date
            ).values()
        )

    def _date_investment_dictionary(self,
                                    start_date: pd.Timestamp,
                                    end_date: pd.Timestamp,
                                    ):

        trades = (self.trades.pipe(filter_date_range, start_date=start_date, end_date=end_date)
                             .pipe(filter_trade_executed))

        date_range = pd.date_range(
            start_date,
            end_date,
            freq='D'
        )

        return {day: trades.pipe(filter_open_on_day, day).INVESTMENT.sum() for day in date_range}
