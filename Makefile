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
	#rm -fr htmlcov/
	rm -f test.db
	python -c "from pwman.tests.test_base_ui import TestBaseUI; TestBaseUI.clean_all()"
	python -c "from pwman.tests.test_importer import TestImporter; TestImporter.clean_all()"
	python -c "from pwman.tests.test_config import TestConfig; TestConfig.clean_all()"
	rm -f pwman/tests/test.conf 

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

lint:
	flake8 pwman scripts

test: install clean
	git checkout pwman/tests/pwman.v0.0.8.db
	python setup.py test

test-all:
	tox

coverage-run:
	coverage run --source pwman setup.py test
	coverage report -m
	@coverage html

coverage: coverage-run
	@rm test.db

docs:
	#rm -f docs/manutils.rst
	#rm -f docs/modules.rst
	sphinx-apidoc -o docs/source/ pwman
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	open docs/_build/html/index.html

release: clean
	python setup.py sdist upload
	python setup.py bdist_wheel upload

dist: clean
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install:
	-pip uninstall -y pwman3
	python setup.py -q install 
