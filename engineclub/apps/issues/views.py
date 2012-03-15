from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from accounts.models import get_account
from issues.models import Issue


@login_required
def issue_list(request):

    account = get_account(request.user.id)

    issues = Issue.objects.all()

    return render_to_response('issues/issue_list.html', {
        'account': account,
        'issues': issues,
    }, RequestContext(request))


@login_required
def issue_detail(request, issue_id):

    account = get_account(request.user.id)

    issue = Issue.objects.get_or_404(id=issue_id,
        account=account)

    # if not issue.opened:
    #     alert.mark_read()

    # if request.method == 'POST' and 'resolved' in request.POST:
    #     alert.resolve()
    #     return HttpResponseRedirect(reverse('alerts-list'))

    return render_to_response('issues/issue_detail.html', {
        'account': account,
        'issue': issue,
    }, RequestContext(request))
