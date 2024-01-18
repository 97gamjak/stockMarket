import numpy as np
import warnings
import shutil

from beartype.typing import List
from ib_insync import IB, Contract, util
from xml.etree import ElementTree as ET
from tqdm import tqdm

from stockMarket import __data_path__


class StoreXMLData:
    def __init__(self, tickers: List[str] | str):
        self.tickers = np.atleast_1d(tickers)
        self.fin_statements = {}

    def save_xml_data(self):
        self._get_fin_statements()
        self._save_xml_files()

    def _get_fin_statements(self):

        util.startLoop()

        app = IB()
        app.connect("127.0.0.1", port=7497,
                    clientId=np.random.default_rng().integers(1, 100000))

        self.contracts = []
        for ticker in self.tickers:

            c = Contract()
            c.symbol = ticker
            c.secType = 'STK'
            c.exchange = "SMART"
            c.currency = "USD"

            self.contracts.append(c)

        self._clean_up_contracts()

        for contract in tqdm(self.contracts, desc="Downloading XML data"):

            self.fin_statements[contract.symbol] = app.reqFundamentalData(
                contract, 'ReportsFinStatements', [])

        app.disconnect()

    def _save_xml_files(self):

        data_path = str(__data_path__.joinpath("fin_statements")) + "/"

        for ticker, xml in tqdm(self.fin_statements.items(), desc="Saving XML files"):
            try:
                tree = ET.XML(xml)
            except TypeError:
                warnings.warn(f"Ticker {ticker} has no data")

            with open(data_path + f"{ticker}_fin_statements.xml", "w") as f:
                f.write(ET.tostring(tree, encoding="unicode"))

        for alias_ticker, original_ticker in same_company_tickers.items():
            if original_ticker in self.fin_statements.keys():
                shutil.copyfile(str(data_path + f"{original_ticker}_fin_statements.xml"),
                                str(data_path + f"{alias_ticker}_fin_statements.xml"))

    def _clean_up_contracts(self):
        for contract in self.contracts:
            if contract.symbol in same_company_tickers.keys():
                contract.symbol = same_company_tickers[contract.symbol]
            if contract.symbol in isin_dict.keys():
                contract.secidType = "ISIN"
                contract.secId = isin_dict[contract.symbol]


same_company_tickers = {
    "GOOG": "GOOGL",
    "FOX": "FOXA",
    "NWS": "NWSA",
}

isin_dict = {
}
