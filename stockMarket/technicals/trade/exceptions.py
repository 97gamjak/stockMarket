from .enums import TradeStatus


class TradeNotExecuted(Exception):
    def __init__(self, trade_status: TradeStatus):
        self.trade_status = trade_status
        super().__init__(f"Trade not executed: {trade_status}")
