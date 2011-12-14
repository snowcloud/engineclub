from celery import task

from analytics.models import OverallAnalytics


@task
def overall_stats():

    from datetime import timedelta

    analytics_processor = OverallAnalytics()

    tags = analytics_processor.tag_report()
    curations = analytics_processor.curation_report()
    months_12 = analytics_processor.curations_in_last(timedelta(weeks=52),
        granularity=timedelta(weeks=4))
