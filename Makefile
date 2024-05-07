.DEFAULT_GOAL: all
.PHONY: all requirements tests install github_deployment_frequency_by_org github_deployment_frequency_by_list github_repository_standards
.ONESHELL: all requirements tests install github_deployment_frequency_by_org github_deployment_frequency_by_list github_repository_standards
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

# repository standards
github_repository_standards:
	@env LOG_LEVEL=INFO env GITHUB_ACCESS_TOKEN="${GITHUB_TOKEN}" python ./github_repository_standards.py \
		--repository="ministryofjustice/opg-digideps" \
		--repository="ministryofjustice/opg-lpa"

# deployment frequency examples
github_deployment_frequency_by_org:
	@env LOG_LEVEL=INFO env GITHUB_ACCESS_TOKEN="${GITHUB_TOKEN}" python ./github_deployment_frequency.py \
		--org-team="ministryofjustice:opg" \
		--duration=6

github_deployment_frequency_by_list:
	@env LOG_LEVEL=INFO env GITHUB_ACCESS_TOKEN="${GITHUB_TOKEN}" python ./github_deployment_frequency.py \
		--repo-branch-workflow='ministryofjustice/opg-digideps:main: live$$' \
		--repo-branch-workflow='ministryofjustice/serve-opg:main: live$$' \
		--duration=6
