from django.conf import settings
from django.db import connections, transaction, DEFAULT_DB_ALIAS
from functools import wraps


def autocommit(using=DEFAULT_DB_ALIAS, conditional=None):
    """
    Decorator that sets database-level autocommit and turns off managed
    transactions in Django.

    If ``conditional`` is passed and is a callable, it is called with the
    arguments to the wrapped function and will enable autocommit only if
    True is returned.
    """
    def _autocommit(func):
        @wraps(func)
        def __autocommit(*args, **kwargs):
            # TODO: Testing autocommit on views isn't very useful and
            #       significantly slows down the test suite.  Instead, write
            #       some better tests for this decorator.
            if getattr(settings, 'TEST', False):
                return func(*args, **kwargs)
            if callable(conditional) and not conditional(*args, **kwargs):
                return func(*args, **kwargs)

            if isinstance(using, basestring):
                using_list = [using]
            else:
                using_list = using

            for alias in using_list:
                connection = connections[using]
                connection.set_autocommit()

            try:
                return func(*args, **kwargs)
            except Exception:
                raise
            finally:
                for alias in using_list:
                    connection = connections[using]
                    connection.set_default_commit()

        return transaction.autocommit(__autocommit)

    # This allows you to use @autocommit or @autocommit(using='...') instead
    # of @autocommit().
    if using is None:
        using = DEFAULT_DB_ALIAS
    if callable(using):
        func = using
        using = DEFAULT_DB_ALIAS
        return _autocommit(func)
    return lambda func: _autocommit(func)
