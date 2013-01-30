"""
dsq_postgres.backend.helpers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010-2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

import psycopg2
from django.db.utils import DatabaseError


def can_reconnect(exc):
    if isinstance(exc, psycopg2.InterfaceError):
        return True
    elif isinstance(exc, psycopg2.OperationalError):
        exc_msg = str(exc)
        if "can't fetch default_isolation_level" in exc_msg:
            return True
        elif "can't set datestyle to ISO" in exc_msg:
            return True
        return True
    elif isinstance(exc, DatabaseError):
        exc_msg = str(exc)
        if 'server closed the connection unexpectedly' in exc_msg:
            return True
        elif 'client_idle_timeout' in exc_msg:
            return True
    return False
