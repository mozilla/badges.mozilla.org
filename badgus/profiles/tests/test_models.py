import logging
import json
import urllib
import urlparse

from nose.tools import assert_equal, with_setup, assert_false, eq_, ok_
from nose.plugins.attrib import attr

import mock

from django.conf import settings, UserSettingsHolder
from django.utils.functional import wraps
from django.db import models
from django.contrib.auth.models import User
from django import test
from django.core.cache import cache


from badgus.base.tests import FakeResponse, override_constance_settings
from badgus.profiles.models import UserProfile


class UserProfileTest(test.TestCase):

    def test_create_profile_on_user_created(self):
        """Ensure that a UserProfile is created when User is created"""
        user = User.objects.create_user(
            'auto_tester', 'auto_tester@example.com', 'auto_tester')
        profile = user.get_profile()
        ok_(profile is not None)
        eq_(False, profile.username_changes)

    def test_create_profile_on_access(self):
        """Ensure that a UserProfile is created on access, if missing"""
        user = User.objects.create_user(
            'auto_tester', 'auto_tester@example.com', 'auto_tester')
        profile = user.get_profile()
        profile.delete()
        profile = user.get_profile()
        ok_(profile is not None)
        eq_(False, profile.username_changes)

class VouchedProfileTests(test.TestCase):

    def setUp(self):
        self.vouched_user = User.objects.create_user(
            'vouched_tester', 'vouched@example.com', 'vouched_tester')
        self.unvouched_user = User.objects.create_user(
            'unvouched_tester', 'unvouched@example.com', 'unvouched_tester')
        self.unknown_user = User.objects.create_user(
            'unknown_tester', 'unknown@example.com', 'unknown_tester')

    @override_constance_settings(
        MOZILLIANS_API_BASE_URL = 'https://testapi',
        MOZILLIANS_API_APPNAME='testappname',
        MOZILLIANS_API_KEY='8675309')
    @mock.patch('requests.get')
    def test_vouching(self, mock_requests_get):
        """Exercise is_vouched_mozillian() profile method"""

        cases = (
            # Valid vouched user
            (self.vouched_user, 200, None, True),
            # Valid unvouched user
            (self.unvouched_user, 200, None, False),
            # Unknown user at mozillians
            (self.unknown_user, 200, json.dumps(dict(objects=[])), False),
            # Bad JSON response from API
            (self.vouched_user, 200, 'BADRESPONSE', False),
            # Forbidden resonse from API
            (self.vouched_user, 401, 'FORBIDDEN', False),
        )
        
        # Set up to simulate API requests / responses
        inputs = dict(status_code=200, headers={}, content='')
        outputs = {}
        def my_requests_get(url, headers=None, timeout=None):
            outputs['url'] = url
            outputs['headers'] = headers
            if inputs['content'] is not None:
                content = inputs['content']
            else:
                content = json.dumps(dict(objects=[
                    {"email": inputs['email'],
                     "is_vouched": inputs['vouched']}
                ]))
            return FakeResponse(status_code=200, headers={}, content=content)
        mock_requests_get.side_effect = my_requests_get

        # Iterate through test cases
        for user, status_code, content, expected in cases:
            cache.clear()
            inputs.update(dict(status_code=status_code, content=content,
                               email=user.email, vouched=expected))
            
            # Run the vouching method, ensure expected
            result = user.get_profile().is_vouched_mozillian()
            eq_(expected, result)

            # ensure the URL requested matches expected values
            parsed = urlparse.urlparse(outputs['url'])
            params = urlparse.parse_qs(parsed.query)
            eq_(user.email, params['email'][0])
            eq_('testappname', params['app_name'][0])
            eq_('8675309', params['app_key'][0])
