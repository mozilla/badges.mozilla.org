import logging

from nose.tools import assert_equal, with_setup, assert_false, eq_, ok_
from nose.plugins.attrib import attr

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django import test

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
