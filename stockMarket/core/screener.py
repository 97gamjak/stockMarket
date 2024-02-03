from __future__ import annotations

import numpy as np

from beartype.typing import Dict, List, Callable, Tuple

from .contracts import Contracts
from .contract import Contract


class ScreenerObject:
    def __init__(self,
                 func_string: str,
                 lambda_func: Callable | None = None,
                 description: str | None = None,
                 screener_object: ScreenerObject | None = None,
                 ) -> None:

        self.description = description if description else func_string
        self.func_string = func_string
        self.lambda_func = lambda_func if lambda_func else lambda x: np.atleast_1d(x)[
            0]
        self.screener_object = screener_object
        self.lower_limit_counter = 0
        self.upper_limit_counter = 0

    def check_to_discard(self, contract: Contract) -> bool:
        if self.screener_object:
            self.to_discard = self.screener_object.check_to_discard(contract)
            self.lower_limit_counter = self.screener_object.lower_limit_counter
            self.upper_limit_counter = self.screener_object.upper_limit_counter
        else:
            self.to_discard = True

        return self.to_discard


class EqualityScreenerObject(ScreenerObject):
    def __init__(self,
                 func_string: str,
                 lambda_func: Callable | None = None,
                 description: str | None = None,
                 screener_object: ScreenerObject | None = None,
                 equal_to: float | str | None = None,
                 not_equal_to: float | str | None = None,
                 ) -> None:
        super().__init__(func_string, lambda_func, description, screener_object)
        self.equal_to = equal_to
        if isinstance(self.equal_to, str):
            self.equal_to = self.equal_to.lower()

        self.not_equal_to = not_equal_to
        if isinstance(self.not_equal_to, str):
            self.not_equal_to = self.not_equal_to.lower()

        if self.equal_to is not None and self.not_equal_to is not None:
            raise ValueError("Cannot set both equal_to and not_equal_to")
        elif self.equal_to is None and self.not_equal_to is None:
            raise ValueError("Must set either equal_to or not_equal_to")

    def check_to_discard(self, contract: Contract) -> bool:
        self.to_discard = super().check_to_discard(contract)

        value = self.lambda_func(contract.__getattribute__(self.func_string))
        if isinstance(value, str):
            value = value.lower()

        to_discard = False
        if self.equal_to is not None and value != self.equal_to:
            to_discard = False
        elif self.not_equal_to is not None and value == self.not_equal_to:
            to_discard = False
        else:
            to_discard = True

        self.to_discard &= to_discard

        return self.to_discard


class LimitScreenerObject(ScreenerObject):
    def __init__(self,
                 func_string: str,
                 lambda_func: Callable | None = None,
                 description: str | None = None,
                 screener_object: ScreenerObject | None = None,
                 min_value: float | None = None,
                 max_value: float | None = None,
                 ) -> None:
        super().__init__(func_string, lambda_func, description, screener_object)
        self.min_value = min_value if min_value is not None else -np.inf
        self.max_value = max_value if max_value is not None else np.inf

    def check_to_discard(self, contract: Contract) -> bool:
        self.to_discard = super().check_to_discard(contract)

        value = self.lambda_func(contract.__getattribute__(self.func_string))

        to_discard = False
        if value == "Infinity":
            to_discard = True
        elif np.isnan(value):
            to_discard = False

        elif value <= self.min_value:
            self.lower_limit_counter += 1
            to_discard = True

        elif value >= self.max_value:
            self.upper_limit_counter += 1
            to_discard = True

        self.to_discard &= to_discard

        return self.to_discard


class Screener:
    def __init__(self,
                 contracts: Contracts,
                 ) -> None:

        self.contracts = contracts
        self.screened_contracts = contracts

    def screen(self,
               screener_objects: List[ScreenerObject]) -> Contracts:

        self.screener_objects = screener_objects

        self.screening_details = f"Screener details for {len(self.contracts)} companies:\n\n"

        for screener_object in self.screener_objects:
            remaining_contracts = []
            for contract in self.screened_contracts:

                to_discard = screener_object.check_to_discard(contract)

                if not to_discard:
                    remaining_contracts.append(contract)

            self.screening_details += f"{screener_object.description}:\n"
            self.screening_details += f"    {screener_object.lower_limit_counter} companies discarded for being below {screener_object.min_value}\n"
            self.screening_details += f"    {screener_object.upper_limit_counter} companies discarded for being above {screener_object.max_value}\n\n"

            self.screened_contracts = Contracts(remaining_contracts)

        return self.screened_contracts
