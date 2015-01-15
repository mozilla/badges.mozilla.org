import os.path
from os.path import dirname

from datetime import datetime, timedelta, tzinfo
from time import time, gmtime, strftime

import hashlib
import logging
import requests
import urllib
import json

from urlparse import urljoin

from constance import config as c_config

import bleach

try:
    from commons.urlresolvers import reverse
except ImportError, e:
    from django.core.urlresolvers import reverse

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

try:
    from tower import ugettext_lazy as _
except ImportError, e:
    from django.utils.translation import ugettext_lazy as _

try:
    from PIL import Image
except ImportError:
    import Image

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


MAX_USERNAME_CHANGES = getattr(settings, 'PROFILE_MAX_USERNAME_CHANGES', 3)

IMG_MAX_SIZE = getattr(settings, "PROFILE_IMG_MAX_SIZE", (256, 256))

# Set up a file system for badge uploads that can be kept separate from the
# rest of /media if necessary. Lots of hackery to ensure sensible defaults.
UPLOADS_ROOT = getattr(settings, 'PROFILE_UPLOADS_ROOT',
    os.path.join(getattr(settings, 'MEDIA_ROOT', 'media/'), 'uploads'))
UPLOADS_URL = getattr(settings, 'PROFILE_UPLOADS_URL',
    urljoin(getattr(settings, 'MEDIA_URL', '/media/'), 'uploads/'))
PROFILE_UPLOADS_FS = FileSystemStorage(location=UPLOADS_ROOT,
                                       base_url=UPLOADS_URL)


def scale_image(img_upload, img_max_size):
    """Crop and scale an image file."""
    try:
        img = Image.open(img_upload)
    except IOError:
        return None

    src_width, src_height = img.size
    src_ratio = float(src_width) / float(src_height)
    dst_width, dst_height = img_max_size
    dst_ratio = float(dst_width) / float(dst_height)

    if dst_ratio < src_ratio:
        crop_height = src_height
        crop_width = crop_height * dst_ratio
        x_offset = int(float(src_width - crop_width) / 2)
        y_offset = 0
    else:
        crop_width = src_width
        crop_height = crop_width / dst_ratio
        x_offset = 0
        y_offset = int(float(src_height - crop_height) / 2)

    img = img.crop((x_offset, y_offset,
        x_offset + int(crop_width), y_offset + int(crop_height)))
    img = img.resize((dst_width, dst_height), Image.ANTIALIAS)

    if img.mode != "RGB":
        img = img.convert("RGB")
    new_img = StringIO()
    img.save(new_img, "PNG")
    img_data = new_img.getvalue()

    return ContentFile(img_data)


def mk_upload_to(field_fn):
    """upload_to builder for file upload fields"""
    def upload_to(instance, filename):
        base, slug = instance.get_upload_meta()
        time_now = int(time())
        return '%(base)s/%(slug)s/%(time_now)s_%(field_fn)s' % dict(
            time_now=time_now, slug=slug, base=base, field_fn=field_fn)
    return upload_to


class UserProfile(models.Model):

    user = models.ForeignKey(User, unique=True)

    username_changes = models.IntegerField(default=0)

    is_confirmed = models.BooleanField(default=False)

    display_name = models.CharField(max_length=64, blank=True, null=True,
                                    unique=False)

    avatar = models.ImageField(blank=True, null=True,
                               storage=PROFILE_UPLOADS_FS,
                               upload_to=mk_upload_to('avatar.png'))

    bio = models.TextField(blank=True)
    organization = models.CharField(max_length=255, default='', blank=True)
    location = models.CharField(max_length=255, default='', blank=True)
    
    created = models.DateTimeField(auto_now_add=True, blank=False)
    modified = models.DateTimeField(auto_now=True, blank=False)

    class Meta:
        pass

    def __unicode__(self):
        return (self.display_name and 
                self.display_name or self.user.username)

    def get_absolute_url(self):
        return reverse('profiles.profile_view', 
                       kwargs={'username':self.user.username})

    def get_upload_meta(self):
        return ("profile", self.user.username)

    def allows_edit(self, user):
        if user == self.user:
            return True
        if user.is_staff or user.is_superuser:
            return True
        return False

    @property
    def bio_html(self):
        return bleach.clean(bleach.linkify(self.bio))

    def username_changes_remaining(self):
        return MAX_USERNAME_CHANGES - self.username_changes

    def can_change_username(self, user=None):
        if self.username_changes_remaining() > 0:
            return True
        return False

    def change_username(self, username, user=None):
        if not self.can_change_username(user):
            return False
        if User.objects.filter(username=username).count() > 0:
            return False
        if username != self.user.username:
            self.user.username = username
            self.user.save()
            self.username_changes += 1
            self.save()
        return True

    def clean(self):
        if self.avatar:
            scaled_file = scale_image(self.avatar.file, IMG_MAX_SIZE)
            if not scaled_file:
                raise ValidationError(_('Cannot process image'))
            self.avatar.file = scaled_file

    def is_vouched_mozillian(self):
        """Check whether this profile is associated with a vouched
        mozillians.org profile"""

        MOZILLIANS_API_BASE_URL = c_config.MOZILLIANS_API_BASE_URL
        MOZILLIANS_API_APPNAME = c_config.MOZILLIANS_API_APPNAME
        MOZILLIANS_API_KEY = c_config.MOZILLIANS_API_KEY
        MOZILLIANS_API_CACHE_KEY_PREFIX = c_config.MOZILLIANS_API_CACHE_KEY_PREFIX
        MOZILLIANS_API_CACHE_TIMEOUT = c_config.MOZILLIANS_API_CACHE_TIMEOUT

        if not MOZILLIANS_API_KEY:
            logging.warning("'MOZILLIANS_API_KEY' not set up.")
            return False

        email = self.user.email
        # /api/v1/users/?app_name=foobar&app_key=12345&email=test@example.com
        url = '%s/users/?%s' % (MOZILLIANS_API_BASE_URL, urllib.urlencode({
            'app_name': MOZILLIANS_API_APPNAME,
            'app_key': MOZILLIANS_API_KEY,
            'email': email
        }))

        # Cache the HTTP request to the API to minimize hits
        cache_key = '%s:%s' % (MOZILLIANS_API_CACHE_KEY_PREFIX,
                               hashlib.md5(url.encode('utf-8')).hexdigest())
        content = cache.get(cache_key)
        if not content:
            resp = requests.get(url)
            if not resp.status_code == 200:
                logging.error("Failed request to mozillians.org API: %s" %
                              resp.status_code)
                return False
            else:
                content = resp.content
                cache.set(cache_key, content, MOZILLIANS_API_CACHE_TIMEOUT)

        try:
            content = json.loads(content)
        except ValueError:
            logging.error("Failed parsing mozillians.org response")
            return False

        for obj in content.get('objects', []):
            if obj['email'].lower() == email.lower():
                return obj['is_vouched']

        return False


def autocreate_user_profile(self):
    """Ensure user profile exists when accessed"""
    profile, created = UserProfile.objects.get_or_create(
        user=User.objects.get(id=self.id), 
        defaults=dict())
    return profile


# HACK: monkeypatch User.get_profile to ensure the profile exists
User.get_profile = autocreate_user_profile

# HACK: monkeypatch User.__unicode__ to use profile display_name when available
def user_display_name(self):
    return unicode(self.get_profile())
User.__unicode__ = user_display_name

# HACK: monkeypatch User.get_absolute_url() to return profile URL
def user_get_absolute_url(self):
    return self.get_profile().get_absolute_url()
User.get_absolute_url = user_get_absolute_url
