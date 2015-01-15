import logging

from django.conf import settings
from django.http import (HttpResponseRedirect, HttpResponse,
        HttpResponseForbidden, HttpResponseNotFound, Http404)
from django.shortcuts import get_object_or_404, render_to_response, redirect

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import (require_GET, require_POST,
                                          require_http_methods)

from constance import config as c_config

import badger.views


@require_http_methods(['GET', 'POST'])
@login_required
def create(request):

    # Restrict badge creation to mozillians, if enabled.
    if c_config.BADGER_ALLOW_ADD_ONLY_BY_MOZILLIANS:
        profile = request.user.get_profile()
        if not profile.is_vouched_mozillian():
            return HttpResponseForbidden()

    return badger.views.create(request)
