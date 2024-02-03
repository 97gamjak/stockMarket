import pandas as pd
import numpy as np

from beartype.typing import Dict

from .contracts import Contracts


def growth_y2y(data):
    return -np.diff(data) / data[1:] * 100


def growth_total(data):
    growths = []
    for i in range(len(data)-1):
        growths.append(
            (data[i] - data[-1]) / data[-1] / (len(data) - i - 1) * 100)
    return np.array(growths)


default_df_entries = {
    "Name": "long_name",
    "Sector": "sector",
    "Financial Statement Type": "fin_statement_type",

    "Price": "price",
    "Trailing PE": "trailing_pe",
    "Forward PE": "forward_pe",
    "Market Cap": "market_cap",

    "Dividend Yield": "dividend_yield",
    "Payout Ratio": "payout_ratio",

    "Revenue": "revenue",
    "Revenue Growth": ("revenue", lambda x: growth_total(x)[0]),
    "Revenue Growth Y2Y": ("revenue", lambda x: growth_y2y(x)[0]),

    "Net Income": "net_income",
    "Avg Net Income": ("net_income", np.mean),
    "Min Net Income": ("net_income", np.min),
    "Max Net Income": ("net_income", np.max),

    "EBIT Margin": "ebit_margin",
    "EBITDA Margin": "ebitda_margin",

    "Operating Cash Flow": "operating_cashflow",

    "Equity Ratio": "equity_ratio",

    "Earnings Date": "earnings_date",
    "Ex-Dividend Date": "ex_dividend_date",
}


def contracts_to_df(contracts: Contracts, dict_to_df: Dict = default_df_entries) -> pd.DataFrame:
    df = pd.DataFrame(columns=dict_to_df.keys(), index=contracts.tickers)

    dict_to_df = _prepare_dict_to_df(dict_to_df)

    for key, (value, lambda_func) in dict_to_df.items():
        df[key] = [lambda_func(contract.__getattribute__(value))
                   for contract in contracts]

    df = df.sort_values(by=["Sector", "Financial Statement Type"], ascending=[True, True])

    return df


def _prepare_dict_to_df(dict_to_df: Dict) -> Dict:
    for key, value in dict_to_df.items():
        if not isinstance(value, tuple):
            dict_to_df[key] = (value, lambda x: np.atleast_1d(x)[0])

    return dict_to_df
