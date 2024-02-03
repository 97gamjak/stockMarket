import numpy as np
import pandas as pd
import warnings
import shutil
import filecmp
import os

from beartype.typing import List
from ib_insync import IB, util
from ib_insync import Contract as IBContract
from xml.etree import ElementTree as ET
from tqdm import tqdm

from stockMarket import __data_path__
from stockMarket.core import Contracts, ContractListType, BalanceSheet, CashFlow, init_income_class

data_path = str(__data_path__.joinpath("fin_statements")) + "/"
data_backup_path = str(__data_path__.joinpath("fin_statements/backup")) + "/"
file_ending = "_fin_statements.xml"


class FinReports:

    def __init__(self, contracts: ContractListType):
        self.contracts = Contracts(contracts)

    def populate_contracts(self):
        self.filenames = [data_path + contract.ticker +
                          file_ending for contract in self.contracts]

        self.coa_map = self.build_coa_map()

        for file, contract in zip(self.filenames, self.contracts):

            try:
                tree = ET.parse(file)
            except FileNotFoundError:
                raise FileNotFoundError(
                    f"Ticker {contract.ticker} has no xml file in {data_path}")

            root = tree.getroot()

            coa_type = root.find("StatementInfo/COAType").text

            self.income = init_income_class(coa_type=coa_type)
            self.balance = BalanceSheet(coa_type=coa_type)
            self.cashflow = CashFlow(coa_type=coa_type)

            fin_statements_annual = root.findall(
                "FinancialStatements/AnnualPeriods/FiscalPeriod/[@Type='Annual']")
            self.add_time_periods(fin_statements_annual)
            self.get_income_statement(fin_statements_annual)
            self.get_cashflow_statement(fin_statements_annual)
            self.get_balance_sheet(fin_statements_annual)

            contract.income = self.income
            contract.balance = self.balance
            contract.cashflow = self.cashflow

        return self.contracts

    def build_coa_map(self):
        coa_map = {}
        for file in self.filenames:
            tree = ET.parse(file)
            root = tree.getroot()
            fin_statement = root.find("FinancialStatements")
            map_items = fin_statement.findall(".//*[@coaItem]")
            for map_item in map_items:
                coa_map[map_item.text] = map_item.attrib["coaItem"]

        return coa_map

    def add_time_periods(self, fin_statements_annual: List[ET.Element]):

        fiscal_years = [i.attrib["FiscalYear"]
                        for i in fin_statements_annual]
        fiscal_years = [pd.Timestamp(year).year for year in fiscal_years]

        fiscal_year_end_dates = [i.attrib["EndDate"]
                                 for i in fin_statements_annual]
        fiscal_year_end_dates = [pd.Timestamp(
            date).date() for date in fiscal_year_end_dates]

        self.income.fiscal_years = fiscal_years
        self.income.fiscal_year_end_dates = fiscal_year_end_dates
        self.balance.fiscal_years = fiscal_years
        self.balance.fiscal_year_end_dates = fiscal_year_end_dates
        self.cashflow.fiscal_years = fiscal_years
        self.cashflow.fiscal_year_end_dates = fiscal_year_end_dates

    def get_financials(self, et_element, statement_type, financial_statement):
        for coa_item, func in financial_statement.coa_items.items():
            line_items = [i.find(f"Statement/[@Type='{statement_type}']/lineItem/[@coaCode='{coa_item}']")
                          for i in et_element]
            func.resize(len(line_items), refcheck=False)
            for i, line_item in enumerate(line_items):
                func[i] = float(
                    line_item.text) if line_item is not None else np.nan

    def get_income_statement(self, et_element: List[ET.Element]):
        self.get_financials(et_element, "INC", self.income)

    def get_cashflow_statement(self, et_element: List[ET.Element]):
        self.get_financials(et_element, "CAS", self.cashflow)

    def get_balance_sheet(self, et_element: List[ET.Element]):
        self.get_financials(et_element, "BAL", self.balance)


class StoreXMLData:
    def __init__(self, contracts: ContractListType):
        self.contracts = Contracts(contracts)
        self.tickers = self.contracts.tickers
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
        for contract in self.contracts:

            c = IBContract()
            c.symbol = contract.ticker
            c.secType = 'STK'
            c.exchange = "SMART"

            if contract.currency != "":
                c.currency = contract.currency
            else:
                c.currency = "USD"

            self.ib_contracts.append(c)

        self._clean_up_contracts()

        for contract in tqdm(self.ib_contracts, desc="Downloading XML data"):

            ticker = contract.symbol
            contract.symbol = contract.symbol.split(".")[0]

            self.fin_statements[ticker] = app.reqFundamentalData(
                contract, 'ReportsFinStatements', [])

        app.disconnect()

    def _save_xml_files(self):

        for ticker, xml in tqdm(self.fin_statements.items(), desc="Saving XML files"):

            ticker = ticker.replace(" ", ".")

            try:
                tree = ET.XML(xml)
            except TypeError:
                warnings.warn(f"Ticker {ticker} has no data")

            target_file = data_path + str(ticker) + file_ending
            target_test_file = data_path + str(ticker) + "_test"
            target_backup_file = data_backup_path + str(ticker) + file_ending

            with open(data_path + str(ticker) + "_test", "w") as f:
                f.write(ET.tostring(tree, encoding="unicode"))

            file_exists = os.path.exists(target_file)

            if file_exists:
                if not filecmp.cmp(target_file, target_test_file):
                    shutil.copyfile(target_file, target_backup_file)
                    shutil.copyfile(target_test_file, target_file)
            else:
                shutil.copyfile(target_test_file, target_file)

            os.remove(target_test_file)

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
