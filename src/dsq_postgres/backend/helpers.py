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
        if 'server closed the connection unexpectedly' in str(exc):
            return True
    return False
