from enum import Enum


class ChartEnum(Enum):
    LAST_HIGH = "last high"


class TradeStatus(Enum):
    UNKNOWN = "UNKNOWN"
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    TO_BE_DETERMINED = "TO_BE_DETERMINED"
    NO_ENTRY_WITHIN_NEXT_INTERVAL = "NO_ENTRY_WITHIN_NEXT_INTERVAL"
    AMBIGUOUS_EXIT_DATE = "AMBIGUOUS_EXIT_DATE"
    TP_NOT_FOUND = "TAKE_PROFIT_NOT_FOUND"
    LOW_SL_RATIO_TOO_LARGE = "LOW_STOP_LOSS_RATIO_TOO_LARGE"
    TP_B_TC_B_TO_LOW_RATIO_TOO_SMALL = "TAKE_PROFIT_BODY_TRIGGER_CANDLE_BODY_TO_LOW_RATIO_TOO_SMALL"
    PL_TOO_SMALL = "PROFIT_LOSS_TOO_SMALL"
    PL_TOO_LARGE = "PROFIT_LOSS_TOO_LARGE"

    @classmethod
    def write_description_to_file(cls, file_path: str):
        with open(file_path, "w") as file:
            for status in cls:
                file.write(f"{status.value}:\n")
                file.write(DESCRIPTION_DICT[status.value])
                file.write("\n\n")


DESCRIPTION_DICT = {
    TradeStatus.UNKNOWN.value: r"""
The Trade status is unknown. This is the default status when a trade is created.
In general, this status should not be seen in a trade that has been evaluated.
""",
    TradeStatus.OPEN.value: r"""
The trade is open and has been executed.
This means that the trade has been executed but not exit scenario has been met.
""",
    TradeStatus.CLOSED.value: r"""
The trade has been closed.
This means that the trade has been executed and an exit scenario has been met.
In other words, either the take profit or stop loss has been hit.
""",
    TradeStatus.TO_BE_DETERMINED.value: r"""
The trade status is to be determined.
This status is used when the available information is not enough to determine if
the trade has been executed or not.
In other words, no entry date has been found yet, but the possible date range for
determination of the entry date is still active.
""",
    TradeStatus.NO_ENTRY_WITHIN_NEXT_INTERVAL.value: r"""
This status means that no entry scenario has been met within the next interval (i.e. the entry date range).
""",
    TradeStatus.AMBIGUOUS_EXIT_DATE.value: r"""
The exit date is ambiguous.
This means, that the exit scenario has been met for both the stop loss and the take profit
at the same date (intraday) on a daily chart.
""",
    TradeStatus.TP_NOT_FOUND.value: r"""
The take profit has not been found. This means that no take profit could be calculated.
In other words, if the take profit should be determined via the last high, no last high could be found.
""",
    TradeStatus.LOW_SL_RATIO_TOO_LARGE.value: r"""
This status means that the stop loss to the lowest price ratio is too large.
The lowest low here is the lowest low within the trigger candle and the candle to
determine the take profit (if the take profit is determined via the last high).
""",
    TradeStatus.TP_B_TC_B_TO_LOW_RATIO_TOO_SMALL.value: r"""
This status means that the ratio between the body of the trigger candle and the body of the take profit candle
to the lowest low is too small.
In other words, this status is triggered if the take profit value is too small in relation to the entry price.
""",
    TradeStatus.PL_TOO_SMALL.value: r"""
The profit loss is too small.
This means that the take profit distance to the entry price is too small in relation to the distance 
of the stop loss to the entry price.
""",
    TradeStatus.PL_TOO_LARGE.value: r"""
The profit loss is too large.
This means that the take profit distance to the entry price is too large in relation to the distance
of the stop loss to the entry price.
"""
}
