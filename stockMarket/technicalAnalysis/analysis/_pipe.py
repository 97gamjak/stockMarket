import inspect
import pandas as pd
import numpy as np

from decorator import decorator
from beartype.typing import Optional

from ..trade import TradeOutcome, TradeStatus


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


@decorator
def filter_date_range_decorator(func, *args, **kwargs):
    trades = args[0]
    start_date = kwargs.get('start_date', None)
    end_date = kwargs.get('end_date', None)
    trades = filter_date_range(trades, start_date, end_date)

    return func(trades, *(args[1:]), **kwargs)


@filter_date_range_decorator(kwsyntax=True)
def filter_closed_trades(trades: pd.DataFrame,
                         start_date: Optional[pd.Timestamp] = None,
                         end_date: Optional[pd.Timestamp] = None,
                         ) -> pd.DataFrame:
    return trades[trades.trade_status == TradeStatus.CLOSED]


@filter_date_range_decorator(kwsyntax=True)
def filter_trade_executed(trades: pd.DataFrame,
                          start_date: Optional[pd.Timestamp] = None,
                          end_date: Optional[pd.Timestamp] = None,
                          ) -> pd.DataFrame:
    return trades[np.array([TradeStatus.trade_executed(status) for status in trades.trade_status])]


@filter_date_range_decorator(kwsyntax=True)
def filter_wins(trades: pd.DataFrame,
                start_date: Optional[pd.Timestamp] = None,
                end_date: Optional[pd.Timestamp] = None,
                ) -> pd.DataFrame:
    return trades[trades.outcome_status == TradeOutcome.WIN]


@filter_date_range_decorator(kwsyntax=True)
def filter_losses(trades: pd.DataFrame,
                  start_date: Optional[pd.Timestamp] = None,
                  end_date: Optional[pd.Timestamp] = None,
                  ) -> pd.DataFrame:
    return trades[trades.outcome_status == TradeOutcome.LOSS]


@filter_date_range_decorator(kwsyntax=True)
def filter_open_on_day(trades: pd.DataFrame,
                       day: pd.Timestamp,
                       start_date: Optional[pd.Timestamp] = None,
                       end_date: Optional[pd.Timestamp] = None,
                       ) -> pd.DataFrame:
    return trades[_is_open_on_day(trades, day)]


@filter_date_range_decorator(kwsyntax=True)
def _is_open_on_day(trades: pd.DataFrame,
                    day: pd.Timestamp,
                    start_date: Optional[pd.Timestamp] = None,
                    end_date: Optional[pd.Timestamp] = None,
                    ) -> bool:
    return (trades.ENTRY_date <= day) & (trades.EXIT_date >= day)


@filter_date_range_decorator(kwsyntax=True)
def _is_closed_on_day(trades: pd.DataFrame,
                      day: pd.Timestamp,
                      start_date: Optional[pd.Timestamp] = None,
                      end_date: Optional[pd.Timestamp] = None,
                      ) -> bool:
    return trades.EXIT_date == day
