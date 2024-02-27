import pandas as pd
import numpy as np

from stockMarket.core import Contract
from stockMarket import __data_path__


class DataChecker:
    data_path = __data_path__ / 'alphavantage'

    def __init__(self, contract: Contract):
        self.contract = contract
        self.ticker = self.contract.ticker

        income_file = self.generate_filename(
            self.ticker, 'income', 'annual')
        balance_file = self.generate_filename(
            self.ticker, 'balance', 'annual')
        cashflow_file = self.generate_filename(
            self.ticker, 'cashflow', 'annual')

        self.income = self.parse_alphavantage_df(income_file)
        self.balance = self.parse_alphavantage_df(balance_file)
        self.cashflow = self.parse_alphavantage_df(cashflow_file)

    def check_data(self):
        self.fiscal_year_ends = self.contract.fiscal_year_end_dates
        self.fiscal_year_ends = [pd.Timestamp(
            date) for date in self.fiscal_year_ends]

        for ibkr_index, date in enumerate(self.fiscal_year_ends):
            av_data = self.income.loc[date]
            try:
                self.check_data_income(av_data, ibkr_index, date)
            except AssertionError as e:
                print(e)

            av_data = self.balance.loc[date]
            self.check_data_balance(av_data, ibkr_index)

            av_data = self.cashflow.loc[date]
            self.check_data_cashflow(av_data, ibkr_index)

    def check_data_income(self, av_data, ibkr_index, date):
        av_string = 'netIncome'
        av_net_income = av_data[av_string] * 1e-6
        ibkr_net_income = self.contract.net_income[ibkr_index]
        self._assert(av_net_income,
                     av_string,
                     ibkr_net_income,
                     ibkr_index,
                     date
                     )

        av_string = 'totalRevenue'
        av_cost_of_goods_and_services_sold = av_data['costofGoodsAndServicesSold'] * \
            1e-6 if av_data['costofGoodsAndServicesSold'] != "None" else 0
        av_operating_income = av_data['operatingIncome'] * \
            1e-6 if av_data['operatingIncome'] != "None" else 0
        av_selling_general_and_admin = av_data['sellingGeneralAndAdministrative'] * \
            1e-6 if av_data['sellingGeneralAndAdministrative'] != "None" else 0
        print(type(av_data['researchAndDevelopment']))
        av_research_and_development = av_data['researchAndDevelopment'] * \
            1e-6 if av_data['researchAndDevelopment'] != "None" else 0
        av_revenue = av_cost_of_goods_and_services_sold + \
            av_operating_income + av_selling_general_and_admin + av_research_and_development
        ibkr_revenue = self.contract.revenue[ibkr_index]
        self._assert(av_revenue,
                     av_string,
                     ibkr_revenue,
                     ibkr_index,
                     date
                     )

    def check_data_balance(self, data, ibkr_index):
        pass

    def check_data_cashflow(self, data, ibkr_index):
        pass

    def _assert(self, av_value, av_string, ibkr_value, ibkr_index, date, rtol=1e-5):
        percentage_error = (av_value - ibkr_value) / ibkr_value
        condition = np.isclose(av_value, ibkr_value, rtol=rtol)
        assert condition, self.assert_message(
            av_string,
            self.ticker,
            date,
            ibkr_index,
            percentage_error
        )

    def assert_message(self, description, ticker, date, index, percentage_error):
        return f"{description} for {ticker} at {date.date()}, report number {index+1}, {percentage_error:.1%} error"

    def generate_filename(self, ticker, statement_type, period):
        return self.data_path / f'{ticker}_{statement_type}_{period}.csv'

    def parse_alphavantage_df(self, file):
        return pd.read_csv(file, sep="\t", index_col="fiscalDateEnding", parse_dates=True)
