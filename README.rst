disqus-postgres
===============

An enhanced psycopg2 backend for Django. This is more or less a collection of hacks.

It provides the following additionaly features:

- Automatic reconnection when a connection is dropped under various conditions.
- Improved tracebacks for transactional errors (e.g. TransactionAborted)
- Delays SET TIME ZONE until your first query.
- Adds a true @autocommit decorator which forces isolation level changes.

.. note:: This backend was developed against Django 1.2.7, and some of these changes may no longer be relevant in later versions of Django.

Usage
=====

::

    DATABASES = {
        'default': {
            'NAME': 'disqus',
            'BACKEND': 'dsq_postgres.backend',
        },              
    }