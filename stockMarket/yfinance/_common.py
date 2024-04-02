import pandas as pd
import os
import warnings
import yfinance as yf
import datetime as dt

from beartype.typing import Optional

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


def adjust_price_data_from_df(df):
    columns = df.columns
    columns_lower_case = [column.lower() for column in columns]
    df = df.rename(columns=dict(zip(columns, columns_lower_case)))
    return df


def get_daily_candle_range(
    ticker: str,
    start_date: dt.date,
    end_date: Optional[dt.date] = None,
    auto_adjust: bool = False
):

    ticker = yf.Ticker(ticker)

    pricing_data = ticker.history(
        start=str(start_date),
        end=str(end_date) if end_date is not None else None,
        auto_adjust=auto_adjust,
        rounding=True,
    )

    return adjust_price_data_from_df(pricing_data)


def get_weekly_candle_range(
        ticker: str,
        start_date: dt.date,
        end_date: Optional[dt.date] = None,
        auto_adjust: bool = False,
        pricing_data: Optional[pd.DataFrame] = None,
):

    if pricing_data is None:
        pricing_data = get_daily_candle_range(
            ticker,
            start_date,
            end_date,
            auto_adjust
        )

    if len(pricing_data) == 0:
        return pricing_data

    weekly_data = pricing_data.resample("W").agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    })

    weekly_data.index = weekly_data.index - pd.Timedelta(days=6)

    return weekly_data
