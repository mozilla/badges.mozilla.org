from django.conf.urls.defaults import *

from django.conf import settings


urlpatterns = patterns('badgus.badger_api.views',
    url(r'^badge/(?P<slug>[^/]+)/awards/?$', 'awards_list',),
)
