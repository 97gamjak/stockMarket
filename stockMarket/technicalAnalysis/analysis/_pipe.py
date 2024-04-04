import pandas as pd

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


def filter_wins(trades: pd.DataFrame) -> pd.DataFrame:
    return trades[trades.outcome_status == TradeOutcome.WIN]


def filter_losses(trades: pd.DataFrame) -> pd.DataFrame:
    return trades[trades.outcome_status == TradeOutcome.LOSS]
