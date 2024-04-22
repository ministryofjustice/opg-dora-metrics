SHELL := $(shell which bash)
OS := $(shell uname | tr '[:upper:]' '[:lower:]')
ARCH := $(shell uname -m)
HOST_ARCH := ${OS}_${ARCH}

.DEFAULT_GOAL: all
.PHONY: all requirements tests install df
.ONESHELL: all requirements tests install df
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
tests:
	env LOG_LEVEL=WARN pytest --log-cli-level=INFO --disable-warnings ./tests/

# Run a series of tests based on name, setup access token
test:
	export LOG_LEVEL=INFO pytest --log-cli-level=INFO -s --disable-warnings ./tests/ -k "$(names)"

# run deployment frequency
df:
	@env LOG_LEVEL=INFO env GITHUB_ACCESS_TOKEN="${GITHUB_TOKEN}" python ./github_deployment_frequency.py \
		--org-team="ministryofjustice:opg" \
		--duration=6
