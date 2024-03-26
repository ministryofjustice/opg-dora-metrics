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

ifeq (, $(shell which poetry))
	$(error poetry command not found)
endif

# Run all tests
tests: install
	pytest --disable-warnings tests/
