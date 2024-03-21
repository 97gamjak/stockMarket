import pandas as pd
import numpy as np
import yfinance as yf

from stockMarket.yfinance._common import adjust_price_data_from_df


def calc_highest_body_price(candle):
    return max(candle.open, candle.close)


def calc_lowest_body_price(candle):
    return min(candle.open, candle.close)


def find_daily_candle(ticker,
                      pricing: pd.DataFrame,
                      candle_index: int,
                      target_price: float,
                      mode=np.greater_equal,
                      min_date=None,
                      ):

    start_date = pricing.index[candle_index].date()
    if candle_index == len(pricing)-1:
        end_date = None
    else:
        # end date can be set to the next candle date for all intervals
        # e.g if interval is weekly than end date is the next week but
        # yf will not include the first day of the next week
        end_date = pricing.index[candle_index + 1].date()
        end_date = str(end_date)

    min_date = min_date if min_date is not None and min_date > start_date else start_date

    if end_date is not None and min_date == end_date:
        return None, None

    ticker = yf.Ticker(ticker)
    pricing_daily = ticker.history(
        auto_adjust=False,
        start=str(min_date),
        end=end_date,
        rounding=True
    )
    pricing_daily = adjust_price_data_from_df(pricing_daily)

    candle = None

    for i in range(len(pricing_daily)):
        candle = pricing_daily.iloc[i]

        check_price = candle.high if mode == np.greater_equal else candle.low

        if mode(candle.open, target_price):
            target_price = candle.open
            break
        elif mode(check_price, target_price):
            break

        candle = None

    if candle is None:
        return None, None
    else:
        return candle, target_price


def find_last_high(
    pricing: pd.DataFrame,
    ref_candle_index: int,
    max_candles: int = 10,
    min_ratio_high_to_ref_candle: float = 1.0,
    max_drawdown_ratio_after_new_high: float = 1.0,
):

    ref_candle = pricing.iloc[ref_candle_index]

    high = ref_candle.high
    high_index = ref_candle_index
    highest_body_price = calc_highest_body_price(ref_candle)

    for i in range(1, max_candles):
        candle_index = ref_candle_index - i
        candle = pricing.iloc[candle_index]
        _highest_body_price = calc_highest_body_price(candle)

        if (high_index == ref_candle_index and candle.high / high > min_ratio_high_to_ref_candle):
            if _highest_body_price / highest_body_price < min_ratio_high_to_ref_candle:
                continue

            high = candle.high
            high_index = candle_index
            highest_body_price = _highest_body_price

        if (high_index != ref_candle_index and candle.high > high):
            high = candle.high
            high_index = candle_index
            highest_body_price = _highest_body_price
        elif high_index != candle_index and (_highest_body_price - ref_candle.low) / (highest_body_price - ref_candle.low) < max_drawdown_ratio_after_new_high:
            break

    if candle_index == high_index:
        return None, None
    else:
        return high, high_index
