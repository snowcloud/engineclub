from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, render
from django.template import RequestContext

from accounts.models import get_account
from invites.forms import InvitationForm, InvitationAcceptForm
from invites.models import Invitation

@user_passes_test(lambda u: u.is_staff)
def index(request):
    objects = Invitation.objects.all()
    context = { 'objects': objects }
    return render_to_response(
        'enginecab/user_invitations.html', 
        context,
        RequestContext(request))


@user_passes_test(lambda u: u.is_staff)
def invite(request):

    account = get_account(request.user.id)

    if request.method == "POST":

        form = InvitationForm(request.POST)

        if form.is_valid():
            invite = Invitation(email=form.cleaned_data['email'],
                invite_from=account)
            invite.save()
            invite.send_email()
            messages.success(request, 'Invitation has been emailed to %s' % invite.email)

            return HttpResponseRedirect(reverse('invitations'))

    else:
        form = InvitationForm()

    return render_to_response('invites/invite.html', {
        'account': account,
        'form': form
    }, RequestContext(request))


def accept(request, code):

    try:
        invitation = Invitation.objects.get(code=code)
        if invitation.accepted:
            return render(request, 'invites/invitation_used.html')
    except Invitation.DoesNotExist:
        raise Http404("Invitation for code not found")

    account = get_account(request.user.id)

    if request.method == "POST":

        form = InvitationAcceptForm(request.POST)

        if form.is_valid():

            user, account = form.save()
            # user.is_staff = True
            user.save()

            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'])
            login(request, user)
            invitation.accepted = True
            invitation.save()
            messages.success(request, 'Welcome to ALISS! Please check your account details below, make any changes, then "Save changes".')

            return HttpResponseRedirect(reverse('youraliss'))

    else:
        form = InvitationAcceptForm()

    return render_to_response('invites/invite.html', {
        'account': account,
        'form': form
    }, RequestContext(request))

def remove(request, object_id):

    try:
        invitation = Invitation.objects.get(id=object_id)
    except Invitation.DoesNotExist:
        raise Http404("Invitation not found")

    if request.method == "POST":
        invitation.delete()
        messages.success(request, 'Invitation deleted')

    return HttpResponseRedirect(reverse('invitations'))


