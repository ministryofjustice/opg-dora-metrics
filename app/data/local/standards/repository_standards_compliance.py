
from app.log.logger import logging
from app.decorator import timer
from app.data.local.github_data.map import RepositoryDetailedAttributes, RepositoryBaselineComplianceAttributes, RepositoryExtendedComplianceAttributes

def repository_standards(local_repository:dict) -> dict:
    """Use the repository passed and field information to determine standards compliance"""
    assert isinstance(local_repository, dict)

    standards:dict = {
        'baseline': {},
        'extended': {},
        'status': {},
        'information': {},
    }
    for field in RepositoryBaselineComplianceAttributes.keys():
        standards['baseline'][field] = local_repository[field]
    for field in RepositoryExtendedComplianceAttributes.keys():
        standards['extended'][field] = local_repository[field]
    # now work out pass status
    for k in ['baseline', 'extended']:
        passed:bool = True
        for v in standards[k].values():
            if v is False:
                passed = False
        standards['status'][k] = passed

    for field in RepositoryDetailedAttributes.keys():
        standards['information'][field] = local_repository[field]

    return standards
