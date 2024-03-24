from stockMarket.utils.enums import StringEnum


class RuleEnum(StringEnum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"

    @classmethod
    def _missing_(cls, value: str) -> "RuleEnum":
        try:
            super()._missing_(value)
        except NotImplementedError:
            raise NotImplementedError(
                f"{value} is not a valid rule enum possible rule enums are {cls.member_repr()} or {cls.value_repr()}")
