import mock
from django.db import connections
from django.test import TransactionTestCase


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
