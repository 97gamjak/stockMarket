from beartype.typing import Optional

from .enums import TradeOutcome, TradeStatus


def check_PL_ratio(
    PL: float,
    min_PL: Optional[float] = None,
    max_PL: Optional[float] = None,
):
    if min_PL is not None and PL < min_PL:
        return TradeStatus.PL_TOO_SMALL

    if max_PL is not None and PL > max_PL:
        return TradeStatus.PL_TOO_LARGE

    return TradeStatus.UNKNOWN


def determine_outcome_status(
    trade_status: TradeStatus,
    ENTRY: float,
    EXIT: float,
) -> TradeOutcome:

    if trade_status == TradeStatus.CLOSED:
        if EXIT > ENTRY:
            return TradeOutcome.WIN

        return TradeOutcome.LOSS

    return TradeOutcome.NONE
