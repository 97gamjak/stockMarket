import numpy as np

from beartype.typing import List
from ib_insync import IB, util
from ib_insync import Contract as IBContract


class RequestHistogramData:
    def __init__(self, contracts: List[str] | str):
        self.tickers = np.atleast_1d(contracts)
        self.data = {}

    def get_data(self, useRTH: bool = True, period: str = "1 Y"):

        util.startLoop()

        app = IB()
        app.connect("127.0.0.1", port=7497,
                    clientId=np.random.default_rng().integers(1, 100000))

        self.ib_contracts = []
        for ticker in self.tickers:

            c = IBContract()
            c.symbol = ticker
            c.secType = 'STK'
            c.exchange = "SMART"
            c.currency = "USD"

            self.ib_contracts.append(c)

        self._clean_up_contracts()

        for contract in self.ib_contracts:

            self.data[contract.symbol] = app.reqHistoricalData(
                contract=contract, endDateTime=None, durationStr=period, barSizeSetting='1 day', whatToShow='MIDPOINT', useRTH=useRTH)

        app.disconnect()

    def _clean_up_contracts(self):
        for contract in self.ib_contracts:
            if contract.symbol in same_company_tickers.keys():
                contract.symbol = same_company_tickers[contract.symbol]
            if contract.symbol in primary_exchange_dict.keys():
                contract.primaryExchange = primary_exchange_dict[contract.symbol]
            if contract.symbol in alternative_tickers.keys():
                contract.symbol = alternative_tickers[contract.symbol]


same_company_tickers = {
    "BRK.B": "BRK A",
    "GOOG": "GOOGL",
    "FOX": "FOXA",
    "NWS": "NWSA",
}

alternative_tickers = {
    "BF.B": "BF B",
}

primary_exchange_dict = {
    "ABNB": "NASDAQ",
    "CAT": "NYSE",
    "CSCO": "NASDAQ",
    "FANG": "NASDAQ",
    "IBM": "NYSE",
    "KEYS": "NYSE",
    "META": "NASDAQ",
    "WELL": "NYSE",
}
