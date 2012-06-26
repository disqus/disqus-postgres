import mock
from django.db import connections
from django.test import TransactionTestCase


class ReconnectTest(TransactionTestCase):
    @mock.patch('dsq_postgres.backend.base.DatabaseWrapper.make_cursor')
    def test_cursor_sends_time_zone_on_first_connect(self, make_cursor):
        c = connections['default']
        cursor = c.cursor()
        cursor.execute('SELECT 1')

        self.assertEquals(make_cursor().execute.call_count, 2)
        make_cursor().execute.assert_any_call('SET TIME ZONE %s', ['America/New_York'])
        make_cursor().execute.assert_any_call('SELECT 1')
