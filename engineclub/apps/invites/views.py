from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from engine_groups.models import get_account
from invites.forms import InvitationForm, InvitationAcceptForm
from invites.models import Invitation


@login_required
def invite(request):

    account = get_account(request.user.id)

    if request.method == "POST":

        form = InvitationForm(request.POST)

        if form.is_valid():
            invite = Invitation(email=form.cleaned_data['email'],
                invite_from=account)
            invite.save()
            invite.send_email()
            return HttpResponseRedirect(reverse('invite'))

    else:
        form = InvitationForm()

    return render_to_response('invites/invite.html', {
        'account': account,
        'form': form
    }, RequestContext(request))


def accept(request, code):

    try:
        invitation = Invitation.objects.get(code=code)
    except Invitation.DoesNotExist:
        raise Http404("Invitation for code not found")

    account = get_account(request.user.id)

    if request.method == "POST":

        form = InvitationAcceptForm(request.POST)

        if form.is_valid():

            user, account = form.save()
            user.is_staff = True
            user.save()

            user = authenticate(username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'])
            login(request, user)
            invitation.delete()
            return HttpResponseRedirect(reverse('cab'))

    else:
        form = InvitationAcceptForm()

    return render_to_response('invites/invite.html', {
        'account': account,
        'form': form
    }, RequestContext(request))
