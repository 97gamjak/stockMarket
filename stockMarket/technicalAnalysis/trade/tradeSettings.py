import json

from beartype.typing import Optional

from .enums import ChartEnum


class TradeSettings:
    def __init__(self,
                 loss_limit: Optional[float] = None,
                 min_PL: Optional[float] = None,
                 max_PL: Optional[float] = None,
                 TP_strategy=ChartEnum.LAST_HIGH,
                 max_CandleDist_TP_ENTRY: int = 10,
                 max_LOW_SL_to_ENTRY_RATIO: Optional[float] = None,
                 min_TP_B_TC_B_to_LOW_RATIO: Optional[float] = 2,
                 min_ratio_high_to_ref_candle: float = 1.0,
                 max_drawdown_ratio_after_new_high: float = 1.0,
                 min_volatility: float = 0.0,
                 ):

        self.loss_limit = loss_limit + 1 if loss_limit is not None else None

        self.min_PL = min_PL
        self.max_PL = max_PL

        self.TP_strategy = TP_strategy
        self.max_CandleDist_TP_ENTRY = max_CandleDist_TP_ENTRY

        self.max_LOW_SL_to_ENTRY_RATIO = max_LOW_SL_to_ENTRY_RATIO
        self.min_TP_B_TC_B_to_LOW_RATIO = min_TP_B_TC_B_to_LOW_RATIO
        self.min_ratio_high_to_ref_candle = min_ratio_high_to_ref_candle
        self.max_drawdown_ratio_after_new_high = max_drawdown_ratio_after_new_high
        self.min_volatility = min_volatility

    def to_json(self):
        return {
            "loss_limit": self.loss_limit,
            "min_PL": self.min_PL,
            "max_PL": self.max_PL,
            "TP_strategy": self.TP_strategy.value,
            "max_CandleDist_TP_ENTRY": self.max_CandleDist_TP_ENTRY,
            "max_LOW_SL_to_ENTRY_RATIO": self.max_LOW_SL_to_ENTRY_RATIO,
            "min_TP_B_TC_B_to_LOW_RATIO": self.min_TP_B_TC_B_to_LOW_RATIO,
            "min_ratio_high_to_ref_candle": self.min_ratio_high_to_ref_candle,
            "max_drawdown_ratio_after_new_high": self.max_drawdown_ratio_after_new_high,
            "min_volatility": self.min_volatility
        }

    def write_to_json_file(self, file_path: str):
        with open(file_path, "w") as file:
            json.dump(self.to_json(), file)

    def from_json_file(self, file_path: str):
        json_file = open(file_path, "r")
        json_dict = json.loads(json_file.read())
        self.from_json(json_dict)

    def from_json(self, json):
        self.loss_limit = json["loss_limit"]
        self.min_PL = json["min_PL"]
        self.max_PL = json["max_PL"]
        self.TP_strategy = ChartEnum(json["TP_strategy"])
        self.max_CandleDist_TP_ENTRY = json["max_CandleDist_TP_ENTRY"]
        self.max_LOW_SL_to_ENTRY_RATIO = json["max_LOW_SL_to_ENTRY_RATIO"]
        self.min_TP_B_TC_B_to_LOW_RATIO = json["min_TP_B_TC_B_to_LOW_RATIO"]
        self.min_ratio_high_to_ref_candle = json["min_ratio_high_to_ref_candle"]
        self.max_drawdown_ratio_after_new_high = json["max_drawdown_ratio_after_new_high"]
        self.min_volatility = json["min_volatility"]

    @classmethod
    def write_description_to_file(cls, file_path: str):
        with open(file_path, "w") as file:
            for key, description in cls.description_dict.items():
                file.write(f"{key}:\n")
                file.write(description)
                file.write("\n\n\n")

    description_dict = {
        "loss_limit": r"""
The maximum loss limit for a trade.
This is the maximum loss that is allowed for a trade.
This means that if the real entry price is above the calculated entry price
the trade will only be executed it the distance to the stop loss relative to the distance
of the entry price to the stop loss is smaller than the loss limit.

For example:
entry_price = 100 (EP)
stop_loss = 90 (SL)
loss_limit = 10% (0.1)

than the maximum real entry price can not exceed:
    (EP - x)/(EP - SL) < loss_limit
    (100 - x)/(100 - 90) < 0.1
    x = (100 - 90)*0.1+100 < 101

Formally, this can be interpreted as a stop limit order with a stop price at 100 and a limit price at 101.
""",

        "min_PL": r"""
The minimum profit loss for a trade.
This is the minimum profit loss that is allowed for a trade.

For example:
entry price = 100 (EP)
stop loss = 90 (SL)

min_PL = 0.3

than the minimum take profit price can not be below:
    (x - EP)/(SL - EP) > min_PL
    (x - 100)/(90 - 100) > 0.3
    x = (90 - 100)*0.3+100 > 97
""",

        "max_PL": r"""
The maximum profit loss for a trade.
This is the maximum profit loss that is allowed for a trade.

For example:
entry price = 100 (EP)
stop loss = 90 (SL)

min_PL = 6

than the maximum take profit price can not be above:
    (x - EP)/(SL - EP) < max_SL_LOW_to_ENTRY_RATIO
    (x - 100)/(90 - 100) < 6
    x = (90 - 100)*6+100 < 60
""",
        "TP_strategy": r"""
The strategy to determine the take profit.
For a more detailed description of the strategies see the ChartEnum class or its respective description file.
""",

        "max_CandleDist_TP_ENTRY": r"""
The maximum distance between the entry price and the take profit price.
This is the maximum number of candles between the entry price and the take profit price.

For example:
entry price = 100 for a candle on the 12.01.2021
take profit price = 110

max_CandleDist_TP_ENTRY = 10

Than the take profit price can not be further away than 10 candles from the entry price in the past in the respective chart (e.g. daily chart, weekly chart, etc.)
""",

        "max_LOW_SL_to_ENTRY_RATIO": r"""
The maximum ratio between the the lowest low to the entry price ratio and stop loss to the entry price.

For example:
entry price = 100 (EP)
stop loss = 90 (SL)

max_SL_LOW_to_ENTRY_RATIO = 2.0

Than the lowest low between the take profit candle and the trigger candle can not be below:
    (x - EP)/(SL - EP) < max_SL_LOW_to_ENTRY_RATIO
    (x - 100)/(90 - 100) < 2.0
    x = (90 - 100)*2+100 < 80
""",

        "min_TP_B_TC_B_to_LOW_RATIO": r"""
The minimum ratio between the body of the take profit price and the body of the trigger candle to the lowest low.

For example:
entry price_body = 100 (EP)
lowest_low = 90 (LL)

min_TP_B_TC_B_to_LOW_RATIO = 2.0

Than the take profit price must be greater than
    (x - LL)/(EP - LL) > min_TP_B_TC_B_to_LOW_RATIO
    (x - 90)/(100 - 90) > 2.0
    x = (100 - 90)*2+90 > 110
""",

        "min_ratio_high_to_ref_candle": r"""
The minimum ratio between the high of the take profit candle and the reference candle.

For example:
reference candle high = 100 (EP)
min_ratio_high_to_ref_candle = 1.03

Then the take profit price must be greater than:
    x/EP > min_ratio_high_to_ref_candle
    x/100 > 1.03
    x = 100*1.03 > 103
""",

        "max_drawdown_ratio_after_new_high": r"""
The maximum drawdown ratio after a new high has been found backwards in time.
This means that if candle i shows a new high, in order to find an even higher high the drawdown ratio between candles i-1,2,3 etc. can not be lower than the max_drawdown_ratio_after_new_high.

For example:
max_drawdown_ratio_after_new_high = 0.95
high = 100 at index i

Than the next high at index i-1 must be greater than:
    x/100 > max_drawdown_ratio_after_new_high
    x/100 > 0.95
    x = 100*0.95 > 95
    
so if candle i-1 has a value of 96 and candle i-2 has a value of 120 than the maximum_drawdown_ratio_after_new_high is fulfilled and candle i-2 is the new high at 120.and

While if candle i-1 has a value of 94 and candle i-2 has a value of 120 than the maximum_drawdown_ratio_after_new_high is not fulfilled and candle i-2 is not the new high and the search for new highs stops and the high at index i is the new high at 100.
""",
        "min_volatility": r"""
The minimum volatility of the candle. This is the minimum distance of the Entry price distance to the stop loss price relative to the entry price.

For example:
entry price = 100 (EP)
min_volatility = 0.1

Than the stop loss price can not be above 90:
    (EP - x)/EP > min_volatility
    (100 - x)/100 > 0.1
    x = 100 - 100*0.1 < 90
"""
    }
