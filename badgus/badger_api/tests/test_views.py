import logging
import hashlib
import json
from base64 import b64encode

from django.conf import settings

from django.http import HttpRequest
from django.test.client import (Client, FakePayload, encode_multipart,
                                BOUNDARY, CONTENT_TYPE_RE, MULTIPART_CONTENT)

from django.contrib.auth.models import User

from nose.tools import assert_equal, with_setup, assert_false, eq_, ok_
from nose.plugins.attrib import attr

from django.template.defaultfilters import slugify

try:
    from badgus.base.urlresolvers import (get_url_prefix, Prefixer, reverse,
                                         set_url_prefix)
    from tower import activate
except ImportError, e:
    from django.core.urlresolvers import reverse
    get_url_prefix = None

from valet_keys.models import Key

from badger.tests import BadgerTestCase

from badger.models import (Badge, Award, Nomination, Progress, DeferredAward,
        NominationApproveNotAllowedException,
        NominationAcceptNotAllowedException,
        BadgeAwardNotAllowedException)
from badger.utils import get_badge, award_badge


class BadgerApiViewsTests(BadgerTestCase):

    def setUp(self):
        self.client = Client()

        self.testuser = self._get_user()

        self.badge = Badge(creator=self.testuser, title="Test II",
                           description="Another test", unique=True)
        self.badge.save()

        self.awards_url = reverse('badger.views.awards_list',
                                  args=(self.badge.slug,))
        
        key = Key()
        key.user = self.testuser
        self.password = key.generate_secret()
        self.username = key.key
        key.save()
        self.key = key

        auth_ct = '%s:%s' % (self.username, self.password)
        self.basic_auth = 'Basic %s' % b64encode(auth_ct)
        self.headers = {'HTTP_AUTHORIZATION': self.basic_auth}

        Award.objects.all().delete()

    def tearDown(self):
        self.key.delete()
        Award.objects.all().delete()
        Badge.objects.all().delete()

    def test_forbidden_without_key(self):
        """POST should require a valid key, or else yield a 403 response"""
        resp = self.client.get(self.awards_url)
        ok_(200, resp.status_code)

        resp = self.client.post(self.awards_url)
        ok_(403, resp.status_code)

        resp = self.client.post(self.awards_url, 
            {'HTTP_AUTHORIZATION': 'Basic THISISINVALID'})
        ok_(403, resp.status_code)

        resp = self.client.post(self.awards_url, self.headers)
        ok_(200, resp.status_code)

        resp = self.client.get(self.awards_url, self.headers)
        ok_(200, resp.status_code)

    def test_bad_data(self):
        """Bad JSON request should result in a 400 response"""
        resp = self.client.post(self.awards_url, "THISISBADDATA",
                         content_type='application/json',
                         HTTP_AUTHORIZATION=self.basic_auth)
        ok_(400, resp.status_code)

    def test_badge_award(self):
        """Can award badges from API"""
        invite_email = 'someguy@example.com'
        invalid_email = 'THISISINVALID'
        description = "Is a hoopy frood."
        award_user = self._get_user(username="awardee1",
                                    email="awardee1@example.com")

        # Construct the request data...
        data = dict(
            description = description,
            emails = [
                award_user.email,
                invite_email,
                invalid_email,
            ],
        )

        # POST to the awards URL
        resp = self.client.post(self.awards_url, json.dumps(data),
                                content_type='application/json',
                                HTTP_AUTHORIZATION=self.basic_auth)
        
        ok_(self.badge.is_awarded_to(award_user))
        award = Award.objects.get(user=award_user, badge=self.badge)
        eq_(description, award.description)

        eq_('application/json', resp['Content-Type'])
        data = json.loads(resp.content)

        ok_('successes' in data)
        ok_(award_user.email in data['successes'])
        eq_('AWARDED', data['successes'][award_user.email])
        ok_(invite_email in data['successes'])
        eq_('INVITED', data['successes'][invite_email])

        ok_('errors' in data)
        ok_(invalid_email in data['errors'])
        eq_('INVALID', data['errors'][invalid_email])

    def test_no_description(self):
        """Awards can be issued with no description"""
        award_user = self._get_user(username="awardee1",
                                    email="awardee1@example.com")

        data = {"emails": [award_user.email]}

        resp = self.client.post(self.awards_url, json.dumps(data),
                                content_type='application/json',
                                HTTP_AUTHORIZATION=self.basic_auth)

        eq_('application/json', resp['Content-Type'])
        data = json.loads(resp.content)
        
        ok_(award_user.email in data['successes'])
        ok_(award_user.email not in data['errors'])
        ok_(self.badge.is_awarded_to(award_user))

    def test_already_awarded(self):
        """Can award badges from API"""
        description = "Is a hoopy frood."
        invite_email = 'someguy@example.com'
        award_user = self._get_user(username="awardee1",
                                    email="awardee1@example.com")

        award = self.badge.award_to(email=award_user.email)
        deferred_award = self.badge.award_to(email=invite_email)

        # Construct the request data...
        data = dict(
            description = description,
            emails = [
                invite_email,
                award_user.email,
            ],
        )

        # POST to the awards URL
        resp = self.client.post(self.awards_url, json.dumps(data),
                                content_type='application/json',
                                HTTP_AUTHORIZATION=self.basic_auth)
        
        eq_('application/json', resp['Content-Type'])
        data = json.loads(resp.content)

        ok_('errors' in data)
        ok_(award_user.email in data['errors'])
        eq_('ALREADYAWARDED', data['errors'][award_user.email])
        ok_(invite_email in data['errors'])
        eq_('ALREADYAWARDED', data['errors'][invite_email])

    def test_disallowed_badge_award(self):
        """User should not be able to POST an award to a badge for which the
        user hasn't got permission to do so"""
        user = self._get_user(username="heyyou",
                              email="heyyou@example.com")
        badge = Badge(creator=user, title="Hey you badge",
                      description="Another test", unique=True)
        badge.save()

        awards_url = reverse('badger.views.awards_list',
                             args=(self.badge.slug,))

        data = dict(emails=['someguy@example.com',])

        resp = self.client.post(awards_url, json.dumps(data),
                                content_type='application/json',
                                HTTP_AUTHORIZATION=self.basic_auth)

        ok_(403, resp.status_code)
