from beartype.typing import List
from enum import Enum


class StringEnum(Enum):
    @classmethod
    def member_repr(cls) -> str:
        return ', '.join([str(member) for member in cls])

    @classmethod
    def value_repr(cls) -> str:
        return ', '.join([str(member.value) for member in cls])

    @classmethod
    def _missing_(cls, value: object):
        """
        This method allows a FileWriteMode to be retrieved from a string.

        Parameters
        ----------
        value : object
            The value to return.
        exception : Exception
            The exception to raise if the value is not found.

        Raises
        ------
        exception
            If the value is not found.
        """
        value = value.lower()

        for member in cls:
            if member.value.lower() == value:
                return member

        raise NotImplementedError(value)

    @classmethod
    def values(cls) -> List[str]:
        return [member.value for member in cls]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)) and not isinstance(other, str):
            return False

        other = type(self)(other)

        return self.value == other.value
