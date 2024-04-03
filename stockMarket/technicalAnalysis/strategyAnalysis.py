import inspect
import pandas as pd

from decorator import decorator, decorate
from beartype.typing import Optional

from .trade import TradeOutcome, TradeStatus


def filter_start_range(
    trades: pd.DataFrame,
    start_date: Optional[pd.Timestamp] = None
) -> pd.DataFrame:

    if start_date is None:
        return trades
    else:
        return trades[trades.TC_date >= start_date]


def filter_end_range(
    trades: pd.DataFrame,
    end_date: Optional[pd.Timestamp] = None
) -> pd.DataFrame:

    if end_date is None:
        return trades
    else:
        return trades[trades.TC_date <= end_date]


def filter_date_range(
    trades: pd.DataFrame,
    start_date: Optional[pd.Timestamp] = None,
    end_date: Optional[pd.Timestamp] = None,
) -> pd.DataFrame:

    return trades.pipe(filter_start_range, start_date).pipe(filter_end_range, end_date)


def filter_closed_trades(trades: pd.DataFrame) -> pd.DataFrame:
    return trades[trades.trade_status == TradeStatus.CLOSED]


def filter_wins(trades: pd.DataFrame) -> pd.DataFrame:
    return trades[trades.outcome_status == TradeOutcome.WIN]


def filter_losses(trades: pd.DataFrame) -> pd.DataFrame:
    return trades[trades.outcome_status == TradeOutcome.LOSS]


@decorator
def select_start_date(func, *args, **kwargs):
    self = args[0]

    if 'start_date' in kwargs:
        start_date = kwargs.get('start_date', None)
        kwargs['start_date'] = start_date if start_date is not None else self.start_date

    return func(*args, **kwargs)


@decorator
def select_end_date(func, *args, **kwargs):
    self = args[0]

    print(args)
    print(kwargs)

    if 'end_date' in kwargs:
        end_date = kwargs.get('end_date', None)
        kwargs['end_date'] = end_date if end_date is not None else self.end_date

    return func(*args, **kwargs)


def select_date_range(func):
    @select_start_date(kwsyntax=True)
    @select_end_date(kwsyntax=True)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def class_decorator(cls):
    for name, method in inspect.getmembers(cls):
        if (not inspect.ismethod(method) and not inspect.isfunction(method)) or inspect.isbuiltin(method):
            continue
        if name.startswith("__") or name.endswith("__"):
            continue

        setattr(cls, name, lambda method: decorate(
            method, select_date_range, kwsyntax=True))
    return cls


@class_decorator
class StrategyAnalysis:
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
                       ) -> float:

        return self.number_of_wins(start_date, end_date) / self.number_of_losses(start_date, end_date)

    def win_rate(self,
                 start_date: Optional[pd.Timestamp] = None,
                 end_date: Optional[pd.Timestamp] = None,
                 ) -> float:

        trades = (self.trades.pipe(filter_date_range, start_date, end_date)
                             .pipe(filter_closed_trades))

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
