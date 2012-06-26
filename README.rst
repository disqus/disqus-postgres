disqus-postgres
===============

An enhanced psycopg2 backend for Django.

It provides the following additionaly features::

- Automatic reconnection when a connection is dropped under various conditions.
- Improved tracebacks for transactional errors (e.g. TransactionAborted)
- Forces SET TIME ZONE and cursors to be entirely lazy.


Usage
=====

::

    DATABASES = {
        'default': {
            'NAME': 'disqus',
            'BACKEND': 'dsq_postgres',
        },              
    }