from datetime import date, datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.utils import simplejson as json

from analytics.models import OverallAnalytics, AccountAnalytics


@login_required
def stat_json(request, stat_name):

    def _parse_date(date_str, default):

        try:
            datetime.strptime(date_str, '%Y-%m-%d').today()
        except ValueError:
            return default

    start = _parse_date(request.GET.get('start', ''), date.today() - timedelta(days=7))
    end = _parse_date(request.GET.get('end', ''), date.today())
    account = request.GET.get('account', '')

    data = {

    }

    if account:
        analytics = AccountAnalytics(account)
    else:
        analytics = OverallAnalytics()

    if not hasattr(analytics, stat_name):
        raise Http404("Stat not found.")

    data = {
        'result': getattr(analytics, stat_name)(start_date=start, end_date=end)
    }

    return HttpResponse(json.dumps(data), mimetype='application/json')


@login_required
def stat_view(request, stat_name):

    return render(request, 'analytics/stat_view.html', {
        'stat_name': stat_name,
        'stat_url': reverse('analytics-json', args=[stat_name, ]),
    })
