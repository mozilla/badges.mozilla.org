from django.conf import settings
from django.conf.urls.defaults import *

from .profiles import urls as profiles_urls

from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()

import badger
badger.autodiscover()

from funfactory import monkeypatches
monkeypatches.patch()

from badger import Progress
#from badger_multiplayer.models import Badge, Award, Nomination
from badger.models import Badge, Award

urlpatterns = patterns('',
    url(r'^$', 'badger.views.home', name='home'),
    (r'^notification/', include('notification.urls')),
    (r'^badges/', include('badger_multiplayer.urls')),
    (r'^badges/', include('badger.urls')),    
    (r'^browserid/', include('django_browserid.urls')),
    (r'^profiles/', include(profiles_urls)),
    (r'^accounts/', include('django.contrib.auth.urls')),    
    (r'^admin/', include(admin.site.urls)),
)

## In DEBUG mode, serve media files through Django.
if settings.DEBUG:
    # Remove leading and trailing slashes so the regex matches.
    media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')
    urlpatterns += patterns('',
        (r'^%s/(?P<path>.*)$' % media_url, 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
