import sys

from dsq_postgres.exceptions import TransactionAborted
from dsq_postgres.helpers import can_reconnect
from functools import wraps


def auto_reconnect_cursor(func):
    """
    Attempt to safely reconnect when an error is hit that resembles the
    bouncer disconnecting the client due to a timeout/etc during a cursor
    execution.
    """
    @wraps(func)
    def inner(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception, e:
            if not can_reconnect(e):
                raise

            self.db.close(reconnect=True)
            self.cursor = self.db._cursor().cursor

            return func(self, *args, **kwargs)

    return inner


def auto_reconnect_connection(func):
    """
    Attempt to safely reconnect when an error is hit that resembles the
    bouncer disconnecting the client due to a timeout/etc.
    """
    @wraps(func)
    def inner(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception, e:
            if not can_reconnect(e):
                raise

            self._cursor = None
            self.close(reconnect=True)

            return func(self, *args, **kwargs)

    return inner


def capture_transaction_exceptions(func):
    """
    Catches database errors and reraises them on subsequent errors that throw
    some cruft about transaction aborted.
    """
    def raise_the_exception(conn, exc):
        if 'current transaction is aborted, commands ignored until end of transaction block' in str(exc):
            exc_info = getattr(conn, '_last_exception', None)
            if exc_info is None:
                raise
            new_exc = TransactionAborted(sys.exc_info(), exc_info)
            raise new_exc.__class__, new_exc, exc_info[2]

        conn._last_exception = sys.exc_info()
        raise

    @wraps(func)
    def inner(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception, e:
            raise_the_exception(self.db, e)

    return inner


def send_set_time_zone(func):
    """
    Lazily sends a SET TIME ZONE command before a query is executed if it
    is pending (e.g. from an isolation level change).
    """
    def set_tz(wrapper, query):
        if not wrapper.db._needs_tz:
            return

        tz_info = wrapper.db.settings_dict.get('TIME_ZONE')
        if not tz_info:
            return

        if query.lower().startswith('SET TIME ZONE '):
            return

        wrapper.cursor.execute("SET TIME ZONE %s", [tz_info])

    @wraps(func)
    def inner(self, query, *args, **kwargs):
        set_tz(self, query)

        try:
            return func(self, query, *args, **kwargs)
        except Exception, e:
            if not can_reconnect(e):
                raise

            self._cursor = None
            self.close(reconnect=True)

            return func(self, query, *args, **kwargs)

    return inner
