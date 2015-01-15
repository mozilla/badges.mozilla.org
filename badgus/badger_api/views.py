import logging
import json

try:
    from cStringIO import cStringIO as StringIO
except:
    from StringIO import StringIO

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import (HttpResponseRedirect, HttpResponse,
        HttpResponseForbidden, HttpResponseNotFound, Http404)
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http.multipartparser import MultiPartParser

from django.utils.translation import ugettext_lazy as _

from valet_keys.decorators import accepts_valet_key

import badger.views

from badger.models import (Badge, Award, Nomination, Progress, DeferredAward,
        BadgerException,
        NominationApproveNotAllowedException,
        NominationAcceptNotAllowedException,
        BadgeAlreadyAwardedException,
        BadgeAwardNotAllowedException)
from badger.utils import get_badge, award_badge


@accepts_valet_key
@csrf_exempt
def awards_list(request, slug=None):
    """Extend the django-badger awards list URL to offer a POST API"""

    if "GET" == request.method or not slug:
        # If GET or missing a slug, bail out to the original view
        return badger.views.awards_list(request, slug)

    if not request.valet_key:
        return HttpResponseForbidden('Valid key required')

    badge = get_object_or_404(Badge, slug=slug)

    if not badge.allows_award_to(request.user):
        return HttpResponseForbidden('Award forbidden')
    
    (data, files, response) = _parse_request_data(request)
    if response: return response

    description = data.get('description', '')
    emails = data.get('emails', [])

    if not emails:
        return _bad_request(_("email list is required"))

    errors, successes = {}, {}

    for email in emails:
        try:
            validate_email(email)
            result = badge.award_to(email=email, awarder=request.user,
                                    description=description,
                                    raise_already_awarded=True)
            if not result:
                errors[email] = 'FAILED'
            else:
                if isinstance(result, Award):
                    successes[email] = 'AWARDED'
                else:
                    successes[email] = 'INVITED'

        except ValidationError, e:
            errors[email] = "INVALID"
        except BadgeAlreadyAwardedException, e:
            errors[email] = "ALREADYAWARDED"
        except Exception, e:
            errors[email] = "EXCEPTION %s" % e

    return _json_response(errors=errors, successes=successes)


def _parse_request_data(request):
    # Try parsing one of the supported content types from the request
    try:
        content_type = request.META.get('CONTENT_TYPE', '')

        if content_type.startswith('application/json'):
            return (json.loads(request.body), None, None)

        elif content_type.startswith('multipart/form-data'):
            parser = MultiPartParser(request.META,
                                     StringIO(request.body),
                                     request.upload_handlers,
                                     request.encoding)
            data, files = parser.parse()
            return (data, files, None)

        else:
            return (None, None,
                    _bad_request(_("Unsupported content-type: %s") %
                                content_type))

    except Exception, e:
        return (None, None,
                _bad_request(_("Request parsing error: %s") % e))


def _bad_request(msg):
    resp = HttpResponse()
    resp.status_code = 400
    resp.content = unicode(msg).encode('utf-8')
    return resp


def _json_response(**out):
    resp = HttpResponse(json.dumps(out))
    resp['Content-Type'] = 'application/json'
    return resp
