from stockMarket.core import Contracts, ContractListType
from stockMarket.yfinance import BasicInfo, Calendar
from stockMarket.ib import FinReports
from stockMarket.utils import Period


def populate_contracts(contracts: ContractListType,
                       include_calendar: bool = True,
                       update_period: str | Period = "monthly",
                       ) -> Contracts:
    contracts = Contracts(contracts)

    contracts = BasicInfo(contracts).get_contract_infos(update=update_period)

    if include_calendar:
        contracts = Calendar(contracts).get_calendar_events(
            update=update_period)

    contracts = FinReports(contracts).populate_contracts()

    return contracts
