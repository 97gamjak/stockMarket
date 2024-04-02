import pandas as pd
import numpy as np

from stockMarket.yfinance._common import get_daily_candle_range
from .enums import TradeStatus, TradeOutcome


def calc_highest_body_price(candle):
    return max(candle.open, candle.close)


def calc_lowest_body_price(candle):
    return min(candle.open, candle.close)


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

        if candle.high > high and _highest_body_price > calc_highest_body_price(ref_candle):
            high = candle.high
            high_index = candle_index
            highest_body_price = _highest_body_price

        if high / ref_candle.high < min_ratio_high_to_ref_candle:
            continue

        elif high_index != candle_index and (_highest_body_price - ref_candle.low) / (highest_body_price - ref_candle.low) < max_drawdown_ratio_after_new_high:
            break

    if ref_candle_index == high_index:
        return None, None
    else:
        return high, high_index
