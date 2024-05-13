.DEFAULT_GOAL: all
.PHONY: all requirements tests install github_deployment_frequency_by_org github_deployment_frequency_by_list github_repository_standards_by_list github_repository_standards_by_org daily_uptime service_uptime
.ONESHELL: all requirements tests install github_deployment_frequency_by_org github_deployment_frequency_by_list github_repository_standards_by_list github_repository_standards_by_org daily_uptime service_uptime
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
	env LOG_LEVEL=INFO pytest --log-cli-level=INFO -s --disable-warnings ./tests/ -k "$(names)"

################
# EXAMPLE USAGE
################

service_uptime:
	@env LOG_LEVEL=INFO env GITHUB_ACCESS_TOKEN="${GITHUB_TOKEN}" python ./service_uptime.py \
		--duration=1

# daily uptime
daily_uptime:
	@aws-vault exec identity -- env LOG_LEVEL=INFO python ./service_uptime_daily.py \
		--service=sirius \
		--role="arn:aws:iam::$(account):role/$(role)"

# repository standards
github_repository_standards_by_list:
	@env LOG_LEVEL=INFO env GITHUB_ACCESS_TOKEN="${GITHUB_TOKEN}" python ./github_repository_standards.py \
		--exclude-archived \
		--repository="ministryofjustice/opg-digideps" \
		--repository="ministryofjustice/opg-lpa" \
		--repository="ministryofjustice/opg-weblate"

github_repository_standards_by_org:
	@env LOG_LEVEL=INFO env GITHUB_ACCESS_TOKEN="${GITHUB_TOKEN}" python ./github_repository_standards.py \
		--exclude-archived \
		--org-team="ministryofjustice:opg"


# deployment frequency examples
github_deployment_frequency_by_org:
	@env LOG_LEVEL=INFO env GITHUB_ACCESS_TOKEN="${GITHUB_TOKEN}" python ./github_deployment_frequency.py \
		--org-team="ministryofjustice:opg" \
		--duration=2

github_deployment_frequency_by_list:
	@env LOG_LEVEL=INFO env GITHUB_ACCESS_TOKEN="${GITHUB_TOKEN}" python ./github_deployment_frequency.py \
		--repo-branch-workflow='ministryofjustice/opg-digideps:main: live$$' \
		--repo-branch-workflow='ministryofjustice/serve-opg:main: live$$' \
		--duration=2
