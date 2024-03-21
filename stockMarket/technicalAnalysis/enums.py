from stockMarket.utils.enums import StringEnum


class StrategyStoringBehavior(StringEnum):
    FULL_OVERWRITE = "full_overwrite"
    MATCHING_OVERWRITE = "matching_overwrite"
    APPEND = "append"
    ABORT = "abort"
    NUMERICAL = "numerical"

    @classmethod
    def _missing_(cls, value: str) -> "StrategyStoringBehavior":
        try:
            super()._missing_(value)
        except NotImplementedError:
            raise NotImplementedError(
                f"{value} is not a valid storing behavior for StrategyFileSettings possible behaviors are {cls.member_repr()} or {cls.value_repr()}")
