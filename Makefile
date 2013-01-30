build:
	pip install -e .
	pip install "file://`pwd`#egg=dsq-postgres[tests]"

test: build
	python runtests.py -x