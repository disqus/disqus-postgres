import mock
import psycopg2
from django.db import connections
from django.test import TransactionTestCase


# These tests are a little bit complicated due to the connection state
class SetTimeZoneTest(TransactionTestCase):
    @mock.patch('dsq_postgres.backend.base.DatabaseWrapper.make_cursor')
    def test_cursor_sends_time_zone_on_first_connect(self, make_cursor):
        c = connections['default']
        c.close()
        cursor = c.cursor()
        cursor.execute('SELECT 1')

        self.assertEquals(make_cursor().execute.call_count, 2)
        make_cursor().execute.assert_any_call('SET TIME ZONE %s', ['America/New_York'])
        make_cursor().execute.assert_any_call('SELECT 1')

    @mock.patch('dsq_postgres.backend.base.DatabaseWrapper.make_cursor')
    def test_only_sends_time_zone_once(self, make_cursor):
        c = connections['default']
        c.close()
        cursor = c.cursor()
        cursor.execute('SELECT 1')
        cursor = c.cursor()
        cursor.execute('SELECT 2')

        self.assertEquals(make_cursor().execute.call_count, 3)
        make_cursor().execute.assert_any_call('SET TIME ZONE %s', ['America/New_York'])
        make_cursor().execute.assert_any_call('SELECT 1')
        make_cursor().execute.assert_any_call('SELECT 2')

    @mock.patch('dsq_postgres.backend.base.DatabaseWrapper.make_cursor')
    def test_sends_timezone_on_reconnect(self, make_cursor):
        c = connections['default']
        c.close()
        cursor = c.cursor()
        cursor.execute('SELECT 1')
        c.close()
        cursor = c.cursor()
        cursor.execute('SELECT 2')

        self.assertEquals(make_cursor().execute.call_count, 4)
        make_cursor().execute.assert_any_call('SET TIME ZONE %s', ['America/New_York'])
        make_cursor().execute.assert_any_call('SELECT 1')
        make_cursor().execute.assert_any_call('SELECT 2')


class ReonnectTest(TransactionTestCase):
    @mock.patch('dsq_postgres.backend.base.DatabaseWrapper.make_cursor')
    def test_does_reconnect_on_interface_error(self, make_cursor):
        calls = [0]

        def error_once(*a, **k):
            if calls[0] > 0:
                return 'foo'
            calls[0] += 1
            raise psycopg2.InterfaceError('herp derp')

        c = connections['default']
        make_cursor().execute.side_effect = error_once
        cursor = c.cursor()
        res = cursor.execute('SELECT 1')
        self.assertEquals(res, 'foo')
