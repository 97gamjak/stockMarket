import inspect

import stockMarket.technicalAnalysis.io.customLogger as customLogger
import stockMarket.technicalAnalysis.io.decorators as decorators

from decorator import decorate


class MetaDecorator(type):
    def __init__(cls, cls_name, bases, attrs):
        for name, method in inspect.getmembers(cls):
            if (not inspect.ismethod(method) and not inspect.isfunction(method)) or inspect.isbuiltin(method):
                continue

            if name.startswith("__") or name.endswith("__"):
                continue

            if name != "real_yield" and name != "predicted_yield":
                continue

            if customLogger.time_logger.getEffectiveLevel() <= 20:
                setattr(cls, name, decorators.timeit(method))

        return super().__init__(cls_name, bases, attrs)
