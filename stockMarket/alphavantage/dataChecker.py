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
            try:
                av_data = self.income.iloc[self.income.index.year ==
                                           date.year].iloc[0]
            except KeyError:
                print(
                    f"Data for {self.ticker} at {date.date()} not found in Alphavantage")
                continue

            try:
                self.check_data_income(av_data, ibkr_index, date)
            except AssertionError as e:
                print(e)

            try:
                av_data = self.balance.iloc[self.balance.index.year ==
                                            date.year].iloc[0]
            except KeyError:
                print(
                    f"Data for {self.ticker} at {date.date()} not found in Alphavantage")
                continue
            self.check_data_balance(av_data, ibkr_index)

            try:
                av_data = self.cashflow.iloc[self.cashflow.index.year ==
                                             date.year].iloc[0]
            except KeyError:
                print(
                    f"Data for {self.ticker} at {date.date()} not found in Alphavantage")
                continue
            self.check_data_cashflow(av_data, ibkr_index)

    def check_data_income(self, av_data, ibkr_index, date):
        # av_string = 'netIncome'
        # av_net_income = av_data[av_string] * 1e-6
        # ibkr_net_income = self.contract.net_income[ibkr_index]
        # self._assert(av_net_income,
        #              av_string,
        #              ibkr_net_income,
        #              ibkr_index,
        #              date
        #              )

        self.check_revenue(av_data, ibkr_index, date)

    def check_revenue(self, av_data, ibkr_index, date):
        av_string = 'totalRevenue'
        av_gross_profit = self.scale_data(
            av_data['grossProfit'], 1e-6)
        av_cost_of_revenue = self.scale_data(
            av_data['costOfRevenue'], 1e-6)
        av_cost_of_goods_and_services_sold = self.scale_data(
            av_data['costofGoodsAndServicesSold'], 1e-6)
        av_operating_income = self.scale_data(
            av_data['operatingIncome'], 1e-6)
        av_selling_general_and_admin = self.scale_data(
            av_data['sellingGeneralAndAdministrative'], 1e-6)
        av_research_and_development = self.scale_data(
            av_data['researchAndDevelopment'], 1e-6)
        av_net_interest_income = self.scale_data(
            av_data['netInterestIncome'], 1e-6)
        av_investment_income_net = self.scale_data(
            av_data['investmentIncomeNet'], 1e-6)
        av_revenue = self.scale_data(av_data["totalRevenue"], 1e-6)

        # if self.ticker not in ["NKE", "INTC"]:
        if self.ticker in ["GOOG"]:
            av_revenue = max(
                av_revenue, av_cost_of_goods_and_services_sold + av_operating_income + av_selling_general_and_admin + av_research_and_development)
        elif self.ticker in ["TT"]:
            av_revenue = av_cost_of_goods_and_services_sold + \
                av_operating_income + av_selling_general_and_admin
        elif self.ticker in []:
            av_revenue = av_cost_of_goods_and_services_sold + \
                av_operating_income + av_selling_general_and_admin + av_research_and_development
        elif self.ticker in ["INTC", "WBA"]:
            av_revenue = av_cost_of_goods_and_services_sold + av_gross_profit
        elif self.ticker in ["NSC"]:
            if av_investment_income_net > 0:
                av_revenue = av_revenue
            else:
                av_revenue = av_revenue - av_net_interest_income
        else:
            av_revenue = av_revenue

        ibkr_revenue = self.contract.revenue[ibkr_index]
        self._assert(av_revenue,
                     av_string,
                     ibkr_revenue,
                     ibkr_index,
                     date,
                     #  rtol=0.02
                     )

    def scale_data(self, data, scale):
        if np.isnan(data):
            return 0
        else:
            return data * scale

    def check_data_balance(self, data, ibkr_index):
        pass

    def check_data_cashflow(self, data, ibkr_index):
        pass

    def _assert(self, av_value, av_string, ibkr_value, ibkr_index, date, rtol=1e-5):
        condition = np.isclose(av_value, ibkr_value, rtol=rtol)
        assert condition, self.assert_message(
            av_string,
            self.ticker,
            date,
            ibkr_index,
            av_value,
            ibkr_value
        )

    def assert_message(self, description, ticker, date, index, av_data, ibkr_data):
        percentage_error = (av_data - ibkr_data) / ibkr_data
        return f"{description} for {ticker} at {date.date()}, report number {index+1}\n{percentage_error:.1%} error in data: {av_data:.2f} vs {ibkr_data:.2f} with diff of {av_data - ibkr_data:.2f}\n"

    def generate_filename(self, ticker, statement_type, period):
        return self.data_path / f'{ticker}_{statement_type}_{period}.csv'

    def parse_alphavantage_df(self, file):
        return pd.read_csv(file, sep="\t", index_col="fiscalDateEnding", parse_dates=True)
