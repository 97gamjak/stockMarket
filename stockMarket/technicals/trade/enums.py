from enum import Enum


class ChartEnum(Enum):
    LAST_HIGH = "last high"


class TradeStatus(Enum):
    UNKNOWN = "unknown"
    TO_BE_DETERMINED = "to be determined"
    NO_ENTRY_WITHIN_NEXT_INTERVAL = "no entry within next interval"
    AMBIGUOUS_EXIT_DATE = "ambiguous exit date"

    TP_NOT_FOUND = "take profit not found"
    LOW_SL_RATIO_TOO_LARGE = "low stop loss ratio too large"
    TP_B_TC_B_TO_LOW_RATIO_TOO_SMALL = "target trigger candle body to low ratio too small"
    PL_TOO_SMALL = "profit loss too small"
    PL_TOO_LARGE = "profit loss too large"
