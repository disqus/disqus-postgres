import sys

from setuptools import setup, find_packages


if 'nosetests' == sys.argv[1]:
    setup_requires = ['nose>=1.0']
else:
    setup_requires = []

tests_require = [
    'django-nose==1.1',
    'nose==1.0',
    'mock==0.8',
]

requires = [
    'psycopg2',
    'Django>=1.3,<1.6',
]

entry_points = {
}


setup(
    name='disqus-postgres',
    version='0.1.0',
    author="DISQUS",
    author_email="dev@disqus.com",
    license='Apache License 2.0',
    package_dir={'': 'src'},
    packages=find_packages("src"),
    install_requires=requires,
    extras_require={
        'tests': tests_require,
    },
    setup_requires=setup_requires,
    test_suite='nose.collector',
    entry_points=entry_points,
    zip_safe=False,
)
