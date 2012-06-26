disqus-postgres
===============

An enhanced psycopg2 backend for Django.

It provides the following additionaly features:

- Automatic reconnection when a connection is dropped under various conditions.
- Improved tracebacks for transactional errors (e.g. TransactionAborted)
- Delays SET TIME ZONE until your first query.
- Adds a true @autocommit decorator which forces isolation level changes.

Usage
=====

::

    DATABASES = {
        'default': {
            'NAME': 'disqus',
            'BACKEND': 'dsq_postgres.backend',
        },              
    }