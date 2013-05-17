build:
	pip install -e . --use-mirrors
	pip install "file://`pwd`#egg=dsq-postgres[tests]" --use-mirrors

test: build
	python runtests.py -x
