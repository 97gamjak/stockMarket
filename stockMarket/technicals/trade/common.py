def calc_highest_body_price(candle):
    return max(candle.open, candle.close)


def calc_lowest_body_price(candle):
    return min(candle.open, candle.close)