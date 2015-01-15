from django.conf import settings
from django.conf.urls import *

from .profiles import urls as profiles_urls

from .base import monkeypatches
monkeypatches.patch()

import badger
badger.autodiscover()

from django.contrib import admin
admin.autodiscover()

from badger import Progress
from badger.models import Badge, Award

urlpatterns = patterns('',
    url(r'^$', 'badger.views.home', name='home'),
    (r'^notification/', include('notification.urls')),
    #(r'^$', include('badgus.base.urls')),
    (r'^badges/create$', 'badgus.base.views.create'),
    (r'^badges/', include('badgus.badger_api.urls')),
    (r'^badges/', include('badger.urls')),
    (r'^profiles/', include(profiles_urls)),
    (r'^accounts/', include('django.contrib.auth.urls')),
    (r'^keys/', include('valet_keys.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^', include('django_browserid.urls')),
)

## In DEBUG mode, serve media files through Django.
if settings.DEBUG:
    # Remove leading and trailing slashes so the regex matches.
    media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')
    urlpatterns += patterns('',
        (r'^%s/(?P<path>.*)$' % media_url, 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
