.DEFAULT_GOAL: all
.PHONY: all requirements test test_with_tokens tests tests_with_tokens install
.ONESHELL: all requirements test test_with_tokens tests tests_with_tokens install
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
	@env LOG_LEVEL=WARN pytest --log-cli-level=INFO --disable-warnings ./tests/
# Run a series of tests based on name, no tokens
test:
	@env LOG_LEVEL=INFO pytest --log-cli-level=INFO -s --disable-warnings ./tests/ -k "$(names)"

# Run all tests, with tokens
tests_with_tokens:
	@env GITHUB_TEST_TOKEN="${GITHUB_TOKEN}" env LOG_LEVEL=WARN pytest --log-cli-level=INFO --disable-warnings ./tests/
# Run a series of tests based on name, setup access token
test_with_tokens:
	@env GITHUB_TEST_TOKEN="${GITHUB_TOKEN}" LOG_LEVEL=INFO pytest --log-cli-level=INFO -s --disable-warnings ./tests/ -k "$(names)"
