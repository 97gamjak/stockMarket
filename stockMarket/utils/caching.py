from decorator import decorator

from beartype.typing import Dict


class Caching:
    cache = {}

    @classmethod
    def clear_cache(cls, cache_type=None):
        if cache_type is None:
            cls.cache = {}
        else:
            cls.cache[cache_type] = None

    @classmethod
    def caching(cls, f, cache_type=None, *args, **kwargs):
        cache_type = cls.infer_cache_type(f, cache_type)

        if cache_type not in cls.cache:
            cls.cache[cache_type] = None

        sub_cache_key = cls.build_sub_cache(cache_type, **kwargs)

        data = cls.get_from_cache(cache_type, sub_cache_key)

        if data is not None:
            kwargs["cache"] = data
            f(*args, **kwargs)
        else:
            data = f(*args, **kwargs)
            cls.add_to_cache(data, cache_type, sub_cache_key)

        return data

    @classmethod
    def infer_cache_type(cls, f, cache_type):
        if cache_type is None:
            cache_type = f.__name__
        return cache_type

    @classmethod
    def build_sub_cache(cls, cache_type, **kwargs):
        if "ticker" in kwargs:
            ticker = kwargs["ticker"]
            if not isinstance(cls.cache[cache_type], Dict):
                cls.cache[cache_type] = {}
            if ticker not in cls.cache[cache_type]:
                cls.cache[cache_type][ticker] = None

            return ticker

        return None

    @classmethod
    def add_to_cache(cls, data, cache_type, sub_cache_key=None):
        if sub_cache_key is None:
            cls.cache[cache_type] = data
        else:
            cls.cache[cache_type][sub_cache_key] = data

    @classmethod
    def get_from_cache(cls, cache_type, sub_cache_key=None):
        if sub_cache_key is None:
            return cls.cache[cache_type]
        return cls.cache[cache_type][sub_cache_key]


def caching(cache_type=None):
    if len(Caching.cache) == 0:
        Caching.cache = {}
    decorator_factory = decorator(Caching.caching, kwsyntax=True)
    return decorator_factory(cache_type=cache_type)
