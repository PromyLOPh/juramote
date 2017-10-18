from functools import wraps

class Busy (Exception):
    pass

def locked (f):
    """
    Per-instance locking for functions
    """

    @wraps(f)
    def decorator(*args, **kwargs):
        self = args[0]
        if not self.lock.acquire (timeout=self.timeout):
            raise Busy ()
        try:
            ret = f(*args, **kwargs)
        finally:
            self.lock.release ()
        return ret
    return decorator

