.PHONY: clean-pyc clean-build docs clean test coverage coverage-run

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "test-all - run tests on every Python version with tox"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "release - package and upload a release"
	@echo "dist - package"

clean_all:
	clean
	clean_docs
	clean_coverage_report

clean: clean-build clean-pyc

clean_docs:
	$(MAKE) -C docs clean

clean_coverage_report:
	rm -rf htmlcov/

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +

lint:
	flake8 pwman scripts

pre-test:
	$(shell sudo service postgresql-9.4 start)
	$(shell sudo service mysql start)
	$(shell sudo service mongodb start)

test: clean install
	python setup.py test
	@rm -f tests/test.conf

test-all:
	tox

coverage-run:
	coverage run -m tests.test_pwman
	coverage report -m
	@coverage html

coverage: coverage-run

docs:
	#rm -f docs/manutils.rst
	#rm -f docs/modules.rst
	sphinx-apidoc -o docs/source/ pwman
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	xdg-open docs/build/html/index.html

release: clean
	python setup.py sdist
	twine upload --skip-existing dist/*

dist: clean
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install:
	pip install -e .
