# Metric reporting for OPG

This repository will supersede the existing [opg-respository-reporting](https://github.com/ministryofjustice/opg-repository-reporting/) with a wider scope of metrics that benefit our teams (some of these being [DORA](https://cloud.google.com/blog/products/devops-sre/using-the-four-keys-to-measure-your-devops-performance) based)and related tooling such as github compositie actions.

## Reports available

Details related to current functionality and there purpose within OPG.

### Deployment frequency

The portfolio function within MoJ request a top level number of production releases per month, normally for the month prior. On top of that, it helps the service teams in areas of delivery improvement and the "agility" of the team. This report produces a historical view of deployments split by month.

`github_deployment_frequency.py` fetches the number of successful releases based on either a passed organisation or a stipulated list of repositorys and workflow names (default to `live$`). It will look for a successful workflow whose name matches the pattern set and if not possible it will fall back to counting merges to the `default_branch` as a proxy measurement as we are fully CI/CD.

As the workflow api has limited filtering abilities, all workflows within a time period are retrieved. The API has an uppoer limit of 1000 per request, so to reduce the odds of data being limited each month is called indvidually. This can cause the generation to be slow.

Output from this report is stored at `./outputs/github_deployment_frequency/*` and should contain `raw.json` and a series of markdown files which can then be pushblised by our documentation site.

There are markdown files for releases per month overall, releases per month per team (github team) and releases per month per repository. Each of these include the total and average per weekday.

For example usage, please check the make targets `github_deployment_frequency_by_org` and `github_deployment_frequency_by_list` and for more details on the command arguments run `python ./github_deployment_frequency.py --help`

*Note: This command does require a github auth token to run*


## Testing

All tests are run within github workflows and you can run them directly via `make tests` or pick a particualr set using `make test names=${PATTERN}`.
