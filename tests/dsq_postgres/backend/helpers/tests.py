import psycopg2
from django.db.utils import DatabaseError
from django.test import TestCase
from dsq_postgres.backend.helpers import can_reconnect


class CanReconnectTest(TestCase):
    def test_can_reconnect_on_interface_error(self):
        exc = psycopg2.InterfaceError('herp derp')
        assert can_reconnect(exc) is True

    def test_can_reconnect_on_default_isolation_level_error(self):
        exc = psycopg2.OperationalError("can't fetch default_isolation_level")
        assert can_reconnect(exc) is True

    def test_can_reconnect_on_datestyle_error(self):
        exc = psycopg2.OperationalError("can't set datestyle to ISO")
        assert can_reconnect(exc) is True

    def test_can_reconnect_on_closed_connection_error(self):
        exc = DatabaseError("server closed the connection unexpectedly")
        assert can_reconnect(exc) is True

    def test_can_reconnect_on_client_idle_timeout_error(self):
        exc = DatabaseError("client_idle_timeout")
        assert can_reconnect(exc) is True

    def test_cannot_reconnect_on_generic_error(self):
        exc = DatabaseError("foo bar")
        assert can_reconnect(exc) is False
