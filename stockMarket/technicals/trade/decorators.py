from decorator import decorator

from .exceptions import TradeNotExecuted
from .enums import TradeStatus


@decorator
def check_trade_status(func, *args, **kwargs):
    self = args[0]
    func(*args, **kwargs)
    if self.trade_status != TradeStatus.UNKNOWN:
        raise TradeNotExecuted(self.trade_status)


@decorator
def ignore_trade_exceptions(func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except TradeNotExecuted:
        pass
