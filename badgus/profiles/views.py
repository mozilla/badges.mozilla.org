from django.conf import settings
from django.db import models

from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth.forms import UserChangeForm

from django.http import (HttpResponseRedirect, HttpResponse,
        HttpResponseForbidden, HttpResponseNotFound)
from django.views.decorators.http import (require_GET, require_POST,
                                          require_http_methods)
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from .models import UserProfile
from .forms import UserProfileEditForm, UserEditForm

try:
    from commons.urlresolvers import reverse
except ImportError, e:
    from django.core.urlresolvers import reverse

try:
    from tower import ugettext_lazy as _
except ImportError, e:
    from django.utils.translation import ugettext_lazy as _


def home(request):
    """Profile home page"""
    if not request.user.is_authenticated():
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL_FAILURE)

    return HttpResponseRedirect(reverse('profiles.profile_view',
            args=(request.user.username,)))


@require_GET
def logout(request):
    """Simple logout view that bounces back to home page"""
    auth_logout(request)
    return HttpResponseRedirect('/')


@require_GET
def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.get_profile()

    return render_to_response('profiles/profile_view.html', dict(
        user=user, profile=profile
    ), context_instance=RequestContext(request))


@require_http_methods(['GET', 'POST'])
@login_required
def profile_edit(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.get_profile()
    if not profile.allows_edit(request.user):
        return HttpResponseForbidden()

    user_form = None

    if request.method != "POST":
        if profile.can_change_username(user):
            user_form = UserEditForm(profile=profile)
        profile_form = UserProfileEditForm(instance=profile)

    else:
        username = profile.user.username
        is_valid = True

        if profile.can_change_username(user):
            user_form = UserEditForm(request.POST, profile=profile)
            if user_form.is_valid():
                username = user_form.cleaned_data['username']
                profile.change_username(username)
            else:
                is_valid = False

        profile_form = UserProfileEditForm(request.POST, request.FILES,
                                           instance=profile)
        if is_valid and profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.save()
            profile_form.save_m2m()
        else:
            is_valid = False

        if is_valid:
            return HttpResponseRedirect(reverse(
                    'profiles.profile_view', args=(username,)))

    return render_to_response('profiles/profile_edit.html', dict(
        user_form=user_form, profile_form=profile_form, 
        user=user, profile=profile,
    ), context_instance=RequestContext(request))
