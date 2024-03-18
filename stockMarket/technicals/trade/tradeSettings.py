from beartype.typing import Optional

from .enums import ChartEnum


class TradeSettings:
    def __init__(self,
                 loss_limit: Optional[float] = None,
                 min_PL: Optional[float] = None,
                 max_PL: Optional[float] = None,
                 TP_strategy=ChartEnum.LAST_HIGH,
                 max_CandleDist_TP_ENTRY: int = 10,
                 max_SL_LOW_to_ENTRY_RATIO: Optional[float] = None,
                 min_TP_B_TC_B_to_LOW_RATIO: Optional[float] = 2,
                 ):

        self.loss_limit = loss_limit + 1 if loss_limit is not None else None

        self.min_PL = min_PL
        self.max_PL = max_PL

        self.TP_strategy = TP_strategy
        self.max_CandleDist_TP_ENTRY = max_CandleDist_TP_ENTRY

        self.max_SL_LOW_to_ENTRY_RATIO = max_SL_LOW_to_ENTRY_RATIO
        self.min_TP_B_TC_B_to_LOW_RATIO = min_TP_B_TC_B_to_LOW_RATIO

    def to_json(self):
        return {
            "loss_limit": self.loss_limit,
            "min_PL": self.min_PL,
            "max_PL": self.max_PL,
            "TP_strategy": self.TP_strategy.value,
            "max_CandleDist_TP_ENTRY": self.max_CandleDist_TP_ENTRY,
            "max_SL_LOW_to_ENTRY_RATIO": self.max_SL_LOW_to_ENTRY_RATIO,
            "min_TP_B_TC_B_to_LOW_RATIO": self.min_TP_B_TC_B_to_LOW_RATIO
        }

    def from_json(self, json):
        self.loss_limit = json["loss_limit"]
        self.min_PL = json["min_PL"]
        self.max_PL = json["max_PL"]
        self.TP_strategy = ChartEnum(json["TP_strategy"])
        self.max_CandleDist_TP_ENTRY = json["max_CandleDist_TP_ENTRY"]
        self.max_SL_LOW_to_ENTRY_RATIO = json["max_SL_LOW_to_ENTRY_RATIO"]
        self.min_TP_B_TC_B_to_LOW_RATIO = json["min_TP_B_TC_B_to_LOW_RATIO"]
