import logging
from github.Repository import Repository
from datetime import date,datetime,timezone
from gh.frequency import year_month_range, status_options

def merged_date_valid(merged_at:date, start:datetime, end:datetime):
    """See if the merged_date is between start & end and not None """

    return (merged_at is not None) and (merged_at >= start and merged_at <= end)


def merges_to_branch(r:Repository, start_date:date, end_date:date, branch:str):
    """Fetches count of merges grouped by month.

    This is used as a proxy measure for those repos that dont use github actions to deploy
    """
    # convert date to datetime
    start:datetime = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0, tzinfo=timezone.utc)
    end:datetime = datetime(end_date.year, end_date.month, end_date.day, 0, 0, 0, tzinfo=timezone.utc)

    logging.info(f"[{r.full_name}] Getting list of merges to [{branch}] between [{start_date}] and [{end_date}]")
    pull_requests = r.get_pulls(state='closed', sort='merged_at', direction='desc', base=branch)
    i:int = 0
    t:int = pull_requests.totalCount
    result:dict = year_month_range(start, end)

    logging.debug(f"[{r.full_name}] found [{t}] total pull requests")
    for pr in pull_requests:
        i = i + 1
        valid = merged_date_valid(pr.merged_at, start, end)
        logging.info(f"[{r.full_name}] [{i}/{t}] PR for [{branch}]@[{pr.merged_at}] is [{valid}]")

        if valid:
            key = pr.merged_at.strftime('%Y-%m')
            if key not in result:
                result[key] = dict((k, 0) for k in status_options)
            result[key]['success'] = result[key]['success'] + 1
        # exit the func early if the date is now before the start date
        elif pr.merged_at is not None and pr.merged_at < start:
            return result

    return result
