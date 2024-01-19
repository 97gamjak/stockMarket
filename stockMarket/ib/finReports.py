import numpy as np
import pandas as pd
import warnings
import shutil

from beartype.typing import List
from ib_insync import IB, util
from ib_insync import Contract as IBContract
from xml.etree import ElementTree as ET
from tqdm import tqdm

from stockMarket import __data_path__
from stockMarket.core import Contract

data_path = str(__data_path__.joinpath("fin_statements")) + "/"
file_ending = "_fin_statements.xml"


class FinReports:

    def __init__(self, contracts: List[str] | str | Contract | List[Contract]):
        contracts = np.atleast_1d(contracts)

        if isinstance(contracts[0], str):
            self.contracts = np.array(
                [Contract(ticker=contract) for contract in contracts])

        else:
            self.contracts = contracts

    def populate_contracts(self):
        self.filenames = [data_path + contract.ticker +
                          file_ending for contract in self.contracts]

        self.build_coa_map()

        for file, contract in zip(self.filenames, self.contracts):

            try:
                tree = ET.parse(file)
            except FileNotFoundError:
                raise FileNotFoundError(
                    f"Ticker {contract.ticker} has no xml file in {data_path}")

            root = tree.getroot()
            contract.coa_type = root.find("StatementInfo/COAType").text

            annual_data = root.find("FinancialStatements/AnnualPeriods")
            fiscal_years = [i.attrib["FiscalYear"]
                            for i in annual_data.findall("FiscalPeriod")]
            fiscal_years = [pd.Timestamp(year).year for year in fiscal_years]
            contract.fiscal_years = fiscal_years

            fiscal_year_end_dates = [i.attrib["EndDate"]
                                     for i in annual_data.findall("FiscalPeriod")]
            fiscal_year_end_dates = [pd.Timestamp(
                date).date() for date in fiscal_year_end_dates]
            contract.fiscal_year_end_dates = fiscal_year_end_dates

    def build_coa_map(self):
        self.coa_map = {}
        for file in self.filenames:
            tree = ET.parse(file)
            root = tree.getroot()
            fin_statement = root.find("FinancialStatements")
            line_items = fin_statement.findall(".//*[@coaItem]")
            for line_item in line_items:
                self.coa_map[line_item.text] = line_item.attrib["coaItem"]


class StoreXMLData:
    def __init__(self, contracts: List[str] | str):
        self.tickers = np.atleast_1d(contracts)
        self.fin_statements = {}

    def save_xml_data(self):
        self._get_fin_statements()
        self._save_xml_files()

    def _get_fin_statements(self):

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

        for contract in tqdm(self.ib_contracts, desc="Downloading XML data"):

            self.fin_statements[contract.symbol] = app.reqFundamentalData(
                contract, 'ReportsFinStatements', [])

        app.disconnect()

    def _save_xml_files(self):

        for ticker, xml in tqdm(self.fin_statements.items(), desc="Saving XML files"):

            ticker = ticker.replace(" ", ".")

            try:
                tree = ET.XML(xml)
            except TypeError:
                warnings.warn(f"Ticker {ticker} has no data")

            with open(data_path + str(ticker) + file_ending, "w") as f:
                f.write(ET.tostring(tree, encoding="unicode"))

        for alias_ticker, original_ticker in same_company_tickers.items():
            if original_ticker in self.fin_statements.keys():
                alias_ticker = alias_ticker.replace(" ", ".")
                original_ticker = original_ticker.replace(" ", ".")

                shutil.copyfile(str(data_path + str(original_ticker) + file_ending),
                                str(data_path + str(alias_ticker) + file_ending))

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
