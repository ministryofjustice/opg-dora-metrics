SHELL := $(shell which bash)
OS := $(shell uname | tr '[:upper:]' '[:lower:]')
ARCH := $(shell uname -m)
HOST_ARCH := ${OS}_${ARCH}

.DEFAULT_GOAL: all
.PHONY: all requirements tests install
.ONESHELL: all requirements tests install
.EXPORT_ALL_VARIABLES:

all: requirements

requirements:
ifeq (, $(shell which python))
	$(error python command not found)
endif

# install pip lib
install:
	pip install -r ./requirements.txt > /dev/null

# Run all tests
tests: install
	pytest --log-cli-level=INFO --disable-warnings -s tests/

# Run all tests
test: install
	pytest --log-cli-level=INFO --disable-warnings tests/ -s -k $(tests)
