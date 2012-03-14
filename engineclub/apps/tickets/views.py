from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from accounts.models import get_account
from tickets.models import Alert


@login_required
def alerts_list(request):

    account = get_account(request.user.id)

    alerts = Alert.objects.for_account(account)

    return render_to_response('alerts/alerts_list.html', {
        'account': account,
        'alerts': alerts,
    }, RequestContext(request))


@login_required
def alert_detail(request, alert_id):

    account = get_account(request.user.id)

    alert = Alert.objects.get_or_404(id=alert_id,
        account=account)

    if not alert.opened:
        alert.mark_read()

    if request.method == 'POST' and 'resolved' in request.POST:
        alert.resolve()
        return HttpResponseRedirect(reverse('alerts-list'))

    return render_to_response('alerts/alert_detail.html', {
        'account': account,
        'alert': alert,
    }, RequestContext(request))
