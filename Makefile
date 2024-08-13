.PHONY: clean-pyc clean-build docs clean test coverage coverage-run clean_all
SHELL := /bin/bash
.DEFAULT_GOAL := help

.PHONY: help
help:
	@mh -f $(MAKEFILE_LIST) $(target) || echo "Please install mh from https://github.com/oz123/mh/releases"
ifndef target
	@(which mh > /dev/null 2>&1 && echo -e "\nUse \`make help target=foo\` to learn more about foo.")
endif

help:

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

test-integration: PWMAN_FAILFAST=1 #? stop on first failure
test-integration: clean install
	python -m tests.test_integration

install-integrationtest-deps:
	pip install -r requirements-integration.txt

install-unittest-deps:
	pip install -r requirements-unittest.txt

test-unit: PWMAN_FAILFAST=1 #? stop on first failure
test-unit: clean install ## run the unit tests
	python -m tests.test_pwman
	@rm -f tests/test.conf

test-all: OPTS ?="--parallel -o" #? options to pass to tox
test-all:
	tox $(OPTS)

build-manpage:
	python man-page-builder.py

coverage-run:
	coverage run --append -m tests.test_pwman
	coverage run --append -m tests.test_integration
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

install:
	pip install -e .

docker/build:: TAG ?= latest
docker/build::  ## build a docker image for pwman3 tests
	docker build -t oz123/pwman3:$(TAG) .

infra-compose::  ## start the infrastructure for the tests
	docker compose --profile infra  up -d

test-compose::  ## run all tests in docker compose
	docker compose down -v
	docker compose build
	docker compose up --profile test --abort-on-container-exit
	docker compose down -v

release:
	python -m build

# vim: tabstop=4 shiftwidth=4
