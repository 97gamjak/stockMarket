import time

from decorator import decorator

import stockMarket.technicalAnalysis.io.customLogger as customLogger


@decorator
def timeit(func, *args, **kwargs):
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    customLogger.time_logger.info(
        f'{func.__name__} took {end_time - start_time:.2f} seconds to run')
    return result
