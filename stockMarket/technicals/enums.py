import sys

from enum import Enum
from typing import Any, Type


class PricingEnum(Enum):
    OPEN = "open"
    CLOSE = "close"
    LOW = "low"
    HIGH = "high"

    @classmethod
    def _missing_(cls, value: object, exception: Type[Exception]) -> Any:
        value = value.lower()

        for member in cls:
            print(member, member.value.lower(), value, file=sys.stderr)
            if member.value.lower() == value:
                return member

        raise exception(value, cls)
