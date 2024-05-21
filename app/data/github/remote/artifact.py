from github.Artifact import Artifact
from github.WorkflowRun import WorkflowRun
from app.logger import logging
from app.decorator import timer


@timer
def artifacts(workflow_run:WorkflowRun) -> list[Artifact]:
    """Helper to remove paginatiedlist and use a normal list"""
    logging.debug('getting artifacts', workflow_run=workflow_run.id)
    artifacts:list[Artifact] = [artifact for artifact in workflow_run.get_artifacts()]
    logging.info(f'[{workflow_run.repository.full_name}] (artifacts) found [{len(artifacts)}] artifacts for workflow',
                 repo=workflow_run.repository.full_name,
                 workflow_run=workflow_run.id)

    return artifacts
