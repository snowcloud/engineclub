from celery import task

from analytics.models import OverallAnalytics


@task.task()
def overall_stats():

    from datetime import timedelta

    analytics = OverallAnalytics()

    tags = analytics.tag_report()
    curations = analytics.curation_report()
    months_12 = analytics.curations_in_last(timedelta(weeks=52),
        granularity=timedelta(weeks=4))
    by_postcode = analytics.curations_by_postcode()
