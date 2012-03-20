from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from pymongo.objectid import ObjectId

from accounts.models import get_account
from ecutils.utils import get_one_or_404
from issues.models import Issue, IssueComment, RESOLUTION_FOR_REMOVAL, SEVERITY_CRITICAL
from issues.forms import CommentForm, IssueResolveForm
from issues.templatetags.issues_tags import can_resolve

@login_required
def issue_list(request, template_name='youraliss/issues.html'):

    account = get_account(request.user.id)
    issues = Issue.objects.for_account(account)
    template_context = {'objects': issues}
    return render_to_response(template_name, RequestContext(request, template_context))

@login_required
def issue_detail(request, object_id, template_name='youraliss/issue_detail.html', next='issue_detail'):

    account = get_account(request.user.id)
    issue = get_one_or_404(Issue, id=ObjectId(object_id))

    if request.method == 'POST' and 'message' in request.POST:
        commentform = CommentForm(request.POST)
        if commentform.is_valid():
            comment = IssueComment(
                owner = account,
                message = commentform.cleaned_data['message'],
                )
            issue.comments.append(comment)
            issue.save()
            return HttpResponseRedirect(reverse(next, args=[issue.id]))
    else:
        commentform = CommentForm()

    if request.method == 'POST' and 'resolved' in request.POST:
        if not can_resolve(account, issue):
            raise PermissionDenied()

        form = IssueResolveForm(request.POST)
        if form.is_valid():

            issue.resolved=int(form.cleaned_data['resolved'])
            issue.resolved_message=form.cleaned_data['resolved_message']
            issue.save()

            if issue.resolved == RESOLUTION_FOR_REMOVAL:
                issue.related_document.moderate_as_bad(account)
            elif issue.severity == SEVERITY_CRITICAL:
                issue.related_document.remove_bad_mod()

            return HttpResponseRedirect(reverse(next, args=[issue.id]))
    else:
        form = IssueResolveForm(initial={'resolved': issue.resolved, 'resolved_message': issue.resolved_message})

    template_context = {'object': issue, 'commentform': commentform, 'form': form}
    return render_to_response(template_name, RequestContext(request, template_context))
