from stockMarket.core import Contracts, ContractListType
from stockMarket.yfinance import BasicInfo, Calendar
from stockMarket.ib import FinReports
from stockMarket.utils import Period

from stockMarket.core.pricing import Pricing


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

    for contract in contracts:
        print("test")
        pricing = Pricing(contract.ticker)
        pricing.get_pricing_data()
        contract.full_pricing_info = pricing.prices

    return contracts
