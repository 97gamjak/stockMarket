import os

from decorator import decorator


@decorator
def finalize(func, *args, **kwargs):
    self = args[0]
    func(*args, **kwargs)

    finalize_commands = np.atleast_1d(
        self.finalize_commands) if self.finalize_commands is not None else []

    for command in finalize_commands:
        os.system(command)
