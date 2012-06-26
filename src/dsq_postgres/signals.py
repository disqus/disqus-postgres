from django.dispatch import Signal
from django.db.backends.signals import connection_created

db_reconnect = Signal(providing_args=["connection"])
