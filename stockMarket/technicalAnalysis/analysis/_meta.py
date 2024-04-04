import inspect

from decorator import decorator


class MetaDecorator(type):
    def __init__(cls, cls_name, bases, attrs):
        for name, method in inspect.getmembers(cls):
            if (not inspect.ismethod(method) and not inspect.isfunction(method)) or inspect.isbuiltin(method):
                continue

            if name.startswith("__") or name.endswith("__"):
                continue

            signature = inspect.signature(method)
            _kwargs = {
                name: param.default
                for name, param in signature.parameters.items()
                if param.default != inspect.Parameter.empty
            }

            if {'start_date', 'end_date'}.issubset(_kwargs):
                setattr(cls, name, select_date_range(method))

        return super().__init__(cls_name, bases, attrs)


def select_date_range(func):

    @select_start_date
    @select_end_date
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


@decorator
def select_start_date(func, *args, **kwargs):
    return select_date(func, 'start_date', *args, **kwargs)


@decorator
def select_end_date(func, *args, **kwargs):
    return select_date(func, 'end_date', *args, **kwargs)


def select_date(func, date_str, *args, **kwargs):
    self = args[0]

    _kwargs = get_kwargs_from_signature(func)

    date = _kwargs.get(date_str, None)
    date = date if date is not None else getattr(self, date_str)
    args = update_args(func, args, date_str, date)

    return func(*args, **kwargs)


def get_kwargs_from_signature(func):
    signature = inspect.signature(func)
    _kwargs = {
        name: param.default
        for name, param in signature.parameters.items()
        if param.default != inspect.Parameter.empty
    }

    return _kwargs


def update_args(func, args, key, value):
    args = list(args)
    signature = inspect.signature(func)
    keys = [param.name for param in signature.parameters.values()]
    args_dict = dict(zip(keys, args))
    args_dict[key] = value
    return tuple(args_dict.values())
