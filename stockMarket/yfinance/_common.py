import pandas as pd
import os
import warnings

from beartype.typing import List

from stockMarket.utils import Period
from stockMarket.core import Contracts

tickers_to_change_name = {
    "BRK.B": "BRK-B",
    "BF.B": "BF-B",
    "FOX": "FOXA",
}


def is_csv_file_up_to_date(file: str, update_period: str | Period):
    period = Period(update_period)

    if period.period_time is None:
        return False

    today = pd.Timestamp.today().date()

    if not os.path.exists(file):
        return False

    with open(file, "r") as f:
        last_update = pd.Timestamp.fromisoformat(f.readline().strip()).date()
        return today - last_update < period.period_time


def check_contracts_in_df(contracts: Contracts, df: pd.DataFrame, to_update: bool):

    if not to_update and not all([contract.ticker in df.index for contract in contracts]):
        warnings.warn(
            "Not all tickers are in calendar and the selected update period indicates that the calendar is up to date. Therefore the calendar will not be updated and the missing tickers will be remain empty. To enforce an update the calendar set update to 'now'")


def write_to_csv(df: pd.DataFrame, file: str):
    with open(file, "w") as f:
        f.write(f"{pd.Timestamp.today().isoformat()}\n")
    df.to_csv(file, mode="a")
