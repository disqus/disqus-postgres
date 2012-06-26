#!/usr/bin/env python
import sys
from os.path import dirname, abspath
from optparse import OptionParser

sys.path.insert(0, dirname(abspath(__file__)))

from django.conf import settings

if not settings.configured:
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'dsq_postgres.backend',
                'USER': 'postgres',
                'NAME': 'dsq_postgres',
                'OPTIONS': {
                    'autocommit': True,
                }
            }
        },
        TIME_ZONE='America/New_York',
        INSTALLED_APPS=[],
        ROOT_URLCONF='',
        DEBUG=False,
        TEMPLATE_DEBUG=True,
    )


from django_nose import NoseTestSuiteRunner


def runtests(*test_args, **kwargs):
    if 'south' in settings.INSTALLED_APPS:
        from south.management.commands import patch_for_test_db_setup
        patch_for_test_db_setup()

    if not test_args:
        test_args = ['tests']

    kwargs.setdefault('interactive', False)

    test_runner = NoseTestSuiteRunner(**kwargs)

    failures = test_runner.run_tests(test_args)
    sys.exit(failures)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('--verbosity', dest='verbosity', action='store', default=1, type=int)
    parser.add_options(NoseTestSuiteRunner.options)
    (options, args) = parser.parse_args()

    runtests(*args, **options.__dict__)
