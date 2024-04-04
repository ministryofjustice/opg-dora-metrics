SHELL := $(shell which bash)
OS := $(shell uname | tr '[:upper:]' '[:lower:]')
ARCH := $(shell uname -m)
HOST_ARCH := ${OS}_${ARCH}

.DEFAULT_GOAL: all
.PHONY: all requirements tests install
.ONESHELL: all requirements tests install
.EXPORT_ALL_VARIABLES:

all: requirements install

requirements:
ifeq (, $(shell which python))
	$(error python command not found)
endif

# install pip lib
install:
	pip install -r ./requirements.txt

# Run all tests
tests: export LOG_LEVEL=WARN
tests:
	pytest --disable-warnings -s tests/

tests_with_api_calls: export GITHUB_ACCESS_TOKEN="${GITHUB_TOKEN}"
tests_with_api_calls: export LOG_LEVEL=INFO
tests_with_api_calls:
	pytest --disable-warnings -s tests/

# Run a series of tests based on name, setup access token
test: export GITHUB_ACCESS_TOKEN="${GITHUB_TOKEN}"
test: export LOG_LEVEL=INFO
test:
	pytest --disable-warnings tests/ -s -k $(names)
