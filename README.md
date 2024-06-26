# Metric reporting for OPG

This repository will supersede the existing [opg-respository-reporting](https://github.com/ministryofjustice/opg-repository-reporting/) with a wider scope of metrics that benefit our teams (some of these being [DORA](https://cloud.google.com/blog/products/devops-sre/using-the-four-keys-to-measure-your-devops-performance) based)and related tooling such as github compositie actions.

## Reports available

Details related to current functionality and there purpose within OPG.

### Deployment frequency

The portfolio function within MoJ request a top level number of production releases per month, normally for the month prior. On top of that, it helps the service teams in areas of delivery improvement and the "agility" of the team. This report produces a historical view of deployments split by month.

`github_deployment_frequency.py` fetches the number of successful releases based on either a passed organisation or a stipulated list of repositorys and workflow names (default to `live$`). It will look for a successful workflow whose name matches the pattern set and if not possible it will fall back to counting merges to the `default_branch` as a proxy measurement as we are fully CI/CD.

As the workflow api has limited filtering abilities, all workflows within a time period are retrieved. The API has an uppoer limit of 1000 per request, so to reduce the odds of data being limited each month is called indvidually. This can cause the generation to be slow.

Output from this report is stored at `./outputs/github_deployment_frequency/*` and should contain `raw.json` and a series of markdown files which can then be published by our documentation site.

There are markdown files for releases per month overall, releases per month per team (github team) and releases per month per repository. Each of these include the total and average per weekday.

For example usage, please check the make targets `github_deployment_frequency_by_org` and `github_deployment_frequency_by_list` and for more details on the command arguments run `python ./github_deployment_frequency.py --help`

*Note: This command does require a github auth token to run*

### GitHub Repository Standards

Checks a series of provided repositories against our agreed MoJ standards and an additional set we utilise in OPG.

`github_repository_standards.py` iterates over repositories, gathers information on each compared to the statndards required and tracks if they have passed each type and each category (baseline / extended).

A json file along with a markdown file are generated as the output and found in `./outputs/github_repository_standards/*` which are then published to our technical documentiona site.

For example usage, please check the make targets `github_repository_standards_by_list` and `github_repository_standards_by_org` or for more details run `python ./github_repository_standards.py --help`

*Note: This command does require a github auth token to run*

### Service Uptime

Merges all of the daily service uptime reports into a single view and splits that by month and service for reporting.

`service_uptime.py` allows you to set how far back to fetch records (via `--duration`) buy Github only keeps artifacts for 3 months.

Generates a series of reports under `./outputs/service_uptime/`.

For example usage, please check the make target `service_uptime`or for more details run `python ./github_repository_standards.py --help`.

*Note: This command does require a github auth token to run*


### Daily Service Uptime

Using AWS cloudwatch health checks, this finds all the `HealthCheckPercentageHealthy` metrics for the account (via environment variables) and generates a json file for yesterdays data.

`service_uptime_daily.py` is intended to run daily and then a secondary script will merge the data files and generate a report over a longer time period.

This is due heath check data being kept in AWS for less than 3 months - and these are typically reported on as monthly or quartly.

*Note: This command does require aws access to run*

## Testing

All tests are run within github workflows and you can run them directly via `make tests` or pick a particular set using `make test names=${PATTERN}`.
