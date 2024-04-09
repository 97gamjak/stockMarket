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


def filter_closed_trades(trades: pd.DataFrame) -> pd.DataFrame:

    return trades[trades.trade_status == TradeStatus.CLOSED]


def filter_trade_executed(trades: pd.DataFrame) -> pd.DataFrame:
    return trades[np.array([TradeStatus.trade_executed(status) for status in trades.trade_status])]


def filter_wins(trades: pd.DataFrame) -> pd.DataFrame:
    return trades[trades.outcome_status == TradeOutcome.WIN]


def filter_losses(trades: pd.DataFrame) -> pd.DataFrame:
    return trades[trades.outcome_status == TradeOutcome.LOSS]


def filter_open_on_day(trades: pd.DataFrame,
                       day: pd.Timestamp,
                       ) -> pd.DataFrame:
    return trades[_is_open_on_day(trades, day)]


def _is_open_on_day(trades: pd.DataFrame,
                    day: pd.Timestamp,
                    ) -> bool:
    return (trades.ENTRY_date <= day) & (trades.EXIT_date >= day)


def _is_closed_on_day(trades: pd.DataFrame,
                      day: pd.Timestamp,
                      ) -> bool:
    return trades.EXIT_date == day
