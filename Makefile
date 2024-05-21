.DEFAULT_GOAL: all
.PHONY: all requirements test test_with_tokens tests tests_with_tokens install github_repository_standards_by_list github_repository_standards_by_org github_deployment_frequency_by_org github_deployment_frequency_by_list
.ONESHELL: all requirements test test_with_tokens tests tests_with_tokens install github_repository_standards_by_list github_repository_standards_by_org github_deployment_frequency_by_org github_deployment_frequency_by_list
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
	@clear && env LOG_LEVEL=WARN pytest --log-cli-level=INFO --disable-warnings ./tests/
# Run a series of tests based on name, no tokens
test:
	@clear && env LOG_LEVEL=INFO pytest --log-cli-level=INFO -s --disable-warnings ./tests/ -k "$(names)"

# Run all tests, with tokens
tests_with_tokens:
	@clear && env GITHUB_TEST_TOKEN="${GITHUB_TOKEN}" env LOG_LEVEL=WARN pytest --log-cli-level=INFO --disable-warnings ./tests/
# Run a series of tests based on name, setup access token
test_with_tokens:
	@clear && env GITHUB_TEST_TOKEN="${GITHUB_TOKEN}" LOG_LEVEL=INFO pytest --log-cli-level=INFO -s --disable-warnings ./tests/ -k "$(names)"

################################################
# report commands
################################################
# daily uptime
# account="649098267436" role="breakglass"
daily_uptime:
	@aws-vault exec identity -- env LOG_LEVEL=INFO python ./service_uptime_daily.py \
		--service=sirius \
		--role="arn:aws:iam::$(account):role/$(role)"


# deployment frequency examples
github_deployment_frequency_by_org:
	@clear && env LOG_LEVEL=INFO env GITHUB_ACCESS_TOKEN="${GITHUB_TOKEN}" python ./github_deployment_frequency.py \
		--org-team="ministryofjustice:opg" \
		--duration=6

github_deployment_frequency_by_list:
	@clear && env LOG_LEVEL=INFO env GITHUB_ACCESS_TOKEN="${GITHUB_TOKEN}" python ./github_deployment_frequency.py \
		--repository='ministryofjustice/opg-digideps' \
		--repository='ministryofjustice/opg-data-lpa-store' \
		--duration=1

# standards
github_repository_standards_by_list:
	@clear && env LOG_LEVEL=INFO env GITHUB_ACCESS_TOKEN="${GITHUB_TOKEN}" python ./github_repository_standards.py \
		--exclude-archived \
		--repository="ministryofjustice/opg-digideps" \
		--repository="ministryofjustice/opg-lpa" \
		--repository="ministryofjustice/opg-weblate"

github_repository_standards_by_org:
	@clear && env LOG_LEVEL=INFO env GITHUB_ACCESS_TOKEN="${GITHUB_TOKEN}" python ./github_repository_standards.py \
		--exclude-archived \
		--org-team="ministryofjustice:opg"
