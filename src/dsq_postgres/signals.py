from django.dispatch import Signal
from django.db.backends.signals import connection_created

reconnect_attempt = Signal(providing_args=["connection"])
