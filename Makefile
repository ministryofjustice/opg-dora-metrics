.DEFAULT_GOAL: all
all: requirements install

requirements:
ifeq (, $(shell which python))
	$(error python command not found)
endif

# install pip lib
.PHONY: install
install:
	pip install -r ./requirements.txt

# Run all tests
.PHONY: tests
tests:
	clear && env LOG_LEVEL=WARN pytest --log-cli-level=INFO --disable-warnings ./tests/

# Run a series of tests based on name, setup access token
.PHONY: test
test:
	clear && env LOG_LEVEL=INFO pytest --log-cli-level=INFO -s --disable-warnings ./tests/ -k "$(names)"

.PHONY: tests
tests_with_tokens:
	clear && env GITHUB_TEST_TOKEN="${GITHUB_TOKEN}" env LOG_LEVEL=WARN pytest --log-cli-level=INFO --disable-warnings ./tests/

# Run a series of tests based on name, setup access token
.PHONY: test
test_with_tokens:
	clear && env GITHUB_TEST_TOKEN="${GITHUB_TOKEN}" env LOG_LEVEL=INFO pytest --log-cli-level=INFO -s --disable-warnings ./tests/ -k "$(names)"


################
# EXAMPLE USAGE
################
.PHONY: service_uptime
service_uptime:
	@clear && env LOG_LEVEL=INFO env GITHUB_ACCESS_TOKEN="${GITHUB_TOKEN}" python ./service_uptime.py \
		--duration=1

# daily uptime
.PHONY: daily_uptime
daily_uptime:
	@clear && aws-vault exec identity -- env LOG_LEVEL=INFO python ./service_uptime_daily.py \
		--service=sirius \
		--role="arn:aws:iam::$(account):role/$(role)"

# repository standards
.PHONY: github_repository_standards_by_list
github_repository_standards_by_list:
	@clear && env LOG_LEVEL=INFO env GITHUB_ACCESS_TOKEN="${GITHUB_TOKEN}" python ./github_repository_standards.py \
		--exclude-archived \
		--repository="ministryofjustice/opg-digideps" \
		--repository="ministryofjustice/opg-lpa" \
		--repository="ministryofjustice/opg-weblate"

.PHONY: github_repository_standards_by_org
github_repository_standards_by_org:
	@clear && env LOG_LEVEL=INFO env GITHUB_ACCESS_TOKEN="${GITHUB_TOKEN}" python ./github_repository_standards.py \
		--exclude-archived \
		--org-team="ministryofjustice:opg"


# deployment frequency examples
.PHONY: github_deployment_frequency_by_org
github_deployment_frequency_by_org:
	@clear && env LOG_LEVEL=INFO env GITHUB_ACCESS_TOKEN="${GITHUB_TOKEN}" python ./github_deployment_frequency.py \
		--org-team="ministryofjustice:opg" \
		--duration=2

.PHONY: github_deployment_frequency_by_list
github_deployment_frequency_by_list:
	@clear && env LOG_LEVEL=INFO env GITHUB_ACCESS_TOKEN="${GITHUB_TOKEN}" python ./github_deployment_frequency.py \
		--repo-branch-workflow='ministryofjustice/opg-digideps:main: live$$' \
		--repo-branch-workflow='ministryofjustice/serve-opg:main: live$$' \
		--duration=2
