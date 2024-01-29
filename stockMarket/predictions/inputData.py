from stockMarket.core import Contracts, ContractListType, contracts_to_df
from stockMarket.api import populate_contracts


class InputData:
    def __init__(self, contracts: ContractListType):
        self.contracts = Contracts(contracts)
        self.contracts = populate_contracts(self.contracts)

    def select_data(self):
        self.df = contracts_to_df(self.contracts).sort_values(
            by='Market Cap', ascending=False)

        self.df = self.df.iloc[:100]
