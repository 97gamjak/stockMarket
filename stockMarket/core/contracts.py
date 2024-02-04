from __future__ import annotations

import numpy as np

from beartype.typing import List, TypeVar

from .contract import Contract

ContractListType = TypeVar(
    "ContractListType", List[str], List[Contract], str, Contract, 'Contracts')


class Contracts:
    def __init__(self, contracts: ContractListType):
        if not isinstance(contracts, Contracts):
            contracts = np.atleast_1d(contracts)
            if len(contracts) == 0:
                self.contract_dict = {}
            elif isinstance(contracts[0], str):
                contracts = np.array(
                    [Contract(ticker=contract) for contract in contracts])

            self.contract_dict = {
                contract.ticker: contract for contract in contracts}
        else:
            self.contract_dict = contracts.contract_dict

    def __getitem__(self, key: str | int) -> Contract:
        if isinstance(key, int):
            return list(self.contract_dict.values())[key]
        else:
            return self.contract_dict[key]

    def __iter__(self):
        return iter(self.contract_dict.values())

    def __len__(self):
        return len(self.contract_dict)

    @property
    def tickers(self):
        return list(self.contract_dict.keys())

    @property
    def long_names(self):
        return [contract.long_name for contract in self.contract_dict.values()]

    @property
    def sectors(self):
        return [contract.sector for contract in self.contract_dict.values()]
