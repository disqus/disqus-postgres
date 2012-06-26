import psycopg2 as Database

# Some of these imports are unused, but they are inherited from other engines
# and should be available as part of the backend ``base.py`` namespace.
from django.db.backends.postgresql_psycopg2.base import DatabaseWrapper, \
  DatabaseFeatures, DatabaseOperations, DatabaseClient, DatabaseCreation, \
  DatabaseIntrospection

from dsq_postgres.backend.decorators import capture_transaction_exceptions, auto_reconnect_cursor, \
  send_set_time_zone, auto_reconnect_connection
from dsq_postgres.signals import db_reconnect, connection_created


__all__ = ('DatabaseWrapper', 'DatabaseFeatures', 'DatabaseOperations',
          'DatabaseOperations', 'DatabaseClient', 'DatabaseCreation',
          'DatabaseIntrospection')


class CursorWrapper(object):
    """
    A wrapper around the postgresql_psycopg2 backend which handles various events
    from cursors, such as auto reconnects and lazy time zone evaluation.
    """

    def __init__(self, db, cursor):
        self.db = db
        self.cursor = cursor

    def __getattr__(self, attr):
        return getattr(self.cursor, attr)

    @capture_transaction_exceptions
    @auto_reconnect_cursor
    @send_set_time_zone
    def execute(self, sql, params=None):
        if params is not None:
            return self.cursor.execute(sql, params)
        return self.cursor.execute(sql)

    @capture_transaction_exceptions
    @auto_reconnect_cursor
    @send_set_time_zone
    def executemany(self, sql, paramlist=()):
        return self.cursor.executemany(sql, paramlist)


class DatabaseWrapper(DatabaseWrapper):
    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        ofeatures = self.features
        # XXX: Compatibility with Django 1.3+ (which sends conn as first arg)
        self.features = DatabaseFeatures(self)
        self.features.uses_savepoints = ofeatures.uses_savepoints
        self.features.uses_autocommit = ofeatures.uses_autocommit

        # Do we need to send "SET TIME ZONE?"
        self._needs_tz = True

    @auto_reconnect_connection
    def _set_isolation_level(self, level):
        if getattr(self, 'isolation_level', None) == level:
            return

        # When we change isolation levels we need to ensure we send "SET TIME ZONE" in case
        # we rolled back a transaction and that was part of the rollback
        self._needs_tz = True

        return super(DatabaseWrapper, self)._set_isolation_level(level)

    @auto_reconnect_connection
    def _cursor(self, *args, **kwargs):
        return CursorWrapper(self, self.make_cursor())

    def make_cursor(self):
        """
        Returns a new raw cursor object, forcing a database connection if it
        is not already available.
        """
        settings_dict = self.settings_dict
        if self.connection is None:
            if settings_dict['NAME'] == '':
                from django.core.exceptions import ImproperlyConfigured
                raise ImproperlyConfigured("You need to specify NAME in your Django settings file.")
            conn_params = {
                'database': settings_dict['NAME'],
            }
            conn_params.update(settings_dict['OPTIONS'])
            if 'autocommit' in conn_params:
                del conn_params['autocommit']
            if settings_dict['USER']:
                conn_params['user'] = settings_dict['USER']
            if settings_dict['PASSWORD']:
                conn_params['password'] = settings_dict['PASSWORD']
            if settings_dict['HOST']:
                conn_params['host'] = settings_dict['HOST']
            if settings_dict['PORT']:
                conn_params['port'] = settings_dict['PORT']

            self.connection = Database.connect(**conn_params)
            self.connection.set_client_encoding('UTF8')
            self.connection.set_isolation_level(self.isolation_level)

            connection_created.send(sender=self.__class__, connection=self)

        cursor = self.connection.cursor()
        cursor.tzinfo_factory = None

        return cursor

    def close(self, reconnect=False):
        """
        This ensures we dont error if the connection has already been closed.
        """
        if reconnect:
            db_reconnect.send(sender=type(self), connection=self)

        if self.connection is not None:
            if not self.connection.closed:
                try:
                    self.connection.close()
                except Database.InterfaceError:
                    # connection was already closed by something
                    # like pgbouncer idle timeout.
                    pass
            self.connection = None

    def set_autocommit(self):
        self._set_isolation_level(0)

    def set_default_commit(self, commit=False):
        level = int(not self.settings_dict['OPTIONS'].get('autocommit', False))
        self._set_isolation_level(level)


class DatabaseFeatures(DatabaseFeatures):
    can_return_id_from_insert = True

    def __init__(self, connection):
        self.connection = connection
