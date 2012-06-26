"""
dsq_postgres.signals
~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010-2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from django.dispatch import Signal
from django.db.backends.signals import connection_created

reconnect_attempt = Signal(providing_args=["connection"])
