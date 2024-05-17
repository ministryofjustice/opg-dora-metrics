
from app.log.logger import logging
from app.decorator import timer
from app.data.local.github_data.map import RepositoryDetailedAttributes, RepositoryBaselineComplianceAttributes, RepositoryExtendedComplianceAttributes


__mapped_fields__:dict = {
    'default_branch_is_main': 'Default branch is called main',
    'default_branch_is_protected': 'Default branch is called main',
    'has_issues': 'Issues are enabled',
    'rules_enforced_for_admins': 'Rules enforced for admins',
    'requires_approval': 'Requires approval',
    'has_description': 'Has a description',
    'has_license': 'Has a license',

    'requires_code_owner_approval': 'Requires code owner approval',
    'vulnerability_alerts_enabled': 'Vulnerability alerts are enabled',
    'has_codeowners_in_github_dir': 'Code owners is in .github folder',
    'has_code_of_conduct': 'Code of conduct is present',
    'has_contributing_guide': 'Contributing guide is present',
    'has_readme': 'Readme is present',
}

def repository_standards(local_repository:dict) -> dict:
    """Use the repository passed and field information to determine standards compliance"""
    assert isinstance(local_repository, dict)

    standards:dict = {
        'baseline': {},
        'extended': {},
        'status': {},
        'information': {},
    }
    for f in RepositoryBaselineComplianceAttributes.keys():
        field:str = __mapped_fields__[f] if f in __mapped_fields__.keys() else f
        standards['baseline'][field] = local_repository.get(f, False)
    for f in RepositoryExtendedComplianceAttributes.keys():
        field:str = __mapped_fields__[f] if f in __mapped_fields__.keys() else f
        standards['extended'][field] = local_repository.get(f, False)
    # now work out pass status
    for k in ['baseline', 'extended']:
        passed:bool = True
        for v in standards[k].values():
            if v is False:
                passed = False
        standards['status'][k] = passed

    for field in RepositoryDetailedAttributes.keys():
        standards['information'][field] = local_repository.get(field, None)

    return standards
