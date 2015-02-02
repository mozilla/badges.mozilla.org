# This is your project's main settings file that can be committed to your
# repo. If you need to override a setting locally, use settings_local.py

# Django settings file for a project based on the playdoh template.
# import * into your settings_local.py
import logging
import os
import socket

from django.utils.functional import lazy

import dj_database_url
from decouple import Csv, config

BASE_DIR = ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

def path(*a):
    return os.path.join(ROOT, *a)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

TEMPLATE_DEBUG = config('DEBUG', default=DEBUG, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv(),
    default='badges-dev.allizom.org,badges.allizom.org,badges.mozilla.org')
BROWSERID_AUDIENCES = config('BROWSERID_AUDIENCES', cast=Csv(),
    default=','.join(['https://%s/' % x for x in ALLOWED_HOSTS]))

# For backwards compatability, (projects built based on cloning playdoh)
# we still have to have a ROOT_URLCONF.
# For new-style playdoh projects this will be overridden automatically
# by the new installer
ROOT_URLCONF = '%s.urls' % os.path.basename(ROOT)

# Is this a dev instance?
DEV = False

ADMINS = ()
MANAGERS = ADMINS

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = {
    'default': config(
        'DATABASE_URL',
        default='mysql://root:passwd@db/badges',
        cast=dj_database_url.parse
    )
}

SLAVE_DATABASES = []

DATABASE_ROUTERS = ('multidb.PinningMasterSlaveRouter',)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': config('MEMCACHED', default='127.0.0.1:11211'),
    }
}

EMAIL_BACKEND = config('EMAIL_BACKEND',
        default='django.core.mail.backends.smtp.EmailBackend')

# Site ID is used by Django's Sites framework.
SITE_ID = 1

## Logging
LOG_LEVEL = logging.INFO
HAS_SYSLOG = True
SYSLOG_TAG = "http_app_playdoh"  # Change this after you fork.
LOGGING_CONFIG = None
LOGGING = {}

# CEF Logging
CEF_PRODUCT = 'Playdoh'
CEF_VENDOR = 'Mozilla'
CEF_VERSION = '0'
CEF_DEVICE_VERSION = '0'


# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = config('LANGUAGE_CODE', default='en-us')

TIME_ZONE = config('TIME_ZONE', default='UTC')

USE_I18N = config('USE_I18N', default=True, cast=bool)

USE_L10N = config('USE_L10N', default=True, cast=bool)

USE_TZ = config('USE_TZ', default=True, cast=bool)

# Gettext text domain
TEXT_DOMAIN = 'messages'
STANDALONE_DOMAINS = [TEXT_DOMAIN, 'javascript']
TOWER_KEYWORDS = {'_lazy': None}
TOWER_ADD_HEADERS = True

## Accepted locales

# Tells the product_details module where to find our local JSON files.
# This ultimately controls how LANGUAGES are constructed.
PROD_DETAILS_DIR = path('lib/product_details_json')

# On dev instances, the list of accepted locales defaults to the contents of
# the `locale` directory within a project module or, for older Playdoh apps,
# the root locale directory.  A localizer can add their locale in the l10n
# repository (copy of which is checked out into `locale`) in order to start
# testing the localization on the dev server.
import glob
import itertools
DEV_LANGUAGES = None
try:
    DEV_LANGUAGES = [
        os.path.basename(loc).replace('_', '-')
        for loc in itertools.chain(glob.iglob(ROOT + '/locale/*'),  # old style
                                   glob.iglob(ROOT + '/*/locale/*'))
        if (os.path.isdir(loc) and os.path.basename(loc) != 'templates')
    ]
except OSError:
    pass

# If the locale/ directory isn't there or it's empty, we make sure that
# we always have at least 'en-US'.
if not DEV_LANGUAGES:
    DEV_LANGUAGES = ('en-US',)

# On stage/prod, the list of accepted locales is manually maintained.  Only
# locales whose localizers have signed off on their work should be listed here.
PROD_LANGUAGES = (
    'en-US',
)


def lazy_lang_url_map():
    from django.conf import settings
    langs = settings.DEV_LANGUAGES if settings.DEV else settings.PROD_LANGUAGES
    return dict([(i.lower(), i) for i in langs])

LANGUAGE_URL_MAP = lazy(lazy_lang_url_map, dict)()


# Override Django's built-in with our native names
def lazy_langs():
    from django.conf import settings
    from product_details import product_details
    langs = DEV_LANGUAGES if settings.DEV else settings.PROD_LANGUAGES
    return dict([(lang.lower(), product_details.languages[lang]['native'])
                 for lang in langs if lang in product_details.languages])

LANGUAGES = lazy(lazy_langs, dict)()

# Tells the extract script what files to look for L10n in and what function
# handles the extraction. The Tower library expects this.
DOMAIN_METHODS = {
    'messages': [
        # Searching apps dirs only exists for historic playdoh apps.
        # See playdoh's base settings for how message paths are set.
        ('apps/**.py',
            'tower.management.commands.extract.extract_tower_python'),
        ('apps/**/templates/**.html',
            'tower.management.commands.extract.extract_tower_template'),
        ('templates/**.html',
            'tower.management.commands.extract.extract_tower_template'),
    ],
}

# Paths that don't require a locale code in the URL.
SUPPORTED_NONLOCALES = ['media', 'static', 'admin', 'browserid']


## Media and templates.

STATIC_ROOT = config('STATIC_ROOT', default=os.path.join(BASE_DIR, 'static'))
STATIC_URL = config('STATIC_URL', default='/static/')

MEDIA_ROOT = config('MEDIA_ROOT', default=os.path.join(BASE_DIR, 'media'))
MEDIA_URL = config('MEDIA_URL', default='/media/')

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'jingo.Loader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'session_csrf.context_processor',
    'django.contrib.messages.context_processors.messages',
    'badgus.base.context_processors.i18n',
    'badgus.base.context_processors.globals',
    #'jingo_minify.helpers.build_ids',
)


def get_template_context_processors(exclude=(), append=(),
                        current={'processors': TEMPLATE_CONTEXT_PROCESSORS}):
    """
    Returns TEMPLATE_CONTEXT_PROCESSORS without the processors listed in
    exclude and with the processors listed in append.

    The use of a mutable dict is intentional, in order to preserve the state of
    the TEMPLATE_CONTEXT_PROCESSORS tuple across multiple settings files.
    """

    current['processors'] = tuple(
        [p for p in current['processors'] if p not in exclude]
    ) + tuple(append)

    return current['processors']


TEMPLATE_DIRS = (
    path('templates'),
)

# Storage of static files
COMPRESS_ROOT = STATIC_ROOT
COMPRESS_CSS_FILTERS = (
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter'
)
COMPRESS_PRECOMPILERS = (
    #('text/coffeescript', 'coffee --compile --stdio'),
    ('text/less', 'lessc {infile} {outfile}'),
    #('text/x-sass', 'sass {infile} {outfile}'),
    #('text/x-scss', 'sass --scss {infile} {outfile}'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)


def JINJA_CONFIG():
    # import jinja2
    # from django.conf import settings
    # from caching.base import cache
    config = {'extensions': ['tower.template.i18n', 'jinja2.ext.do',
                             'jinja2.ext.with_', 'jinja2.ext.loopcontrols'],
              'finalize': lambda x: x if x is not None else ''}
#    if 'memcached' in cache.scheme and not settings.DEBUG:
        # We're passing the _cache object directly to jinja because
        # Django can't store binary directly; it enforces unicode on it.
        # Details: http://jinja.pocoo.org/2/documentation/api#bytecode-cache
        # and in the errors you get when you try it the other way.
#        bc = jinja2.MemcachedBytecodeCache(cache._cache,
#                                           "%sj2:" % settings.CACHE_PREFIX)
#        config['cache_size'] = -1 # Never clear the cache
#        config['bytecode_cache'] = bc
    return config


## Middlewares, apps, URL configs.

MIDDLEWARE_CLASSES = (
    'badgus.base.middleware.LocaleURLMiddleware',
    'multidb.middleware.PinningRouterMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'session_csrf.CsrfMiddleware',  # Must be after auth middleware.
    'django.contrib.messages.middleware.MessageMiddleware',
    'commonware.middleware.FrameOptionsHeader',
    'mobility.middleware.DetectMobileMiddleware',
    'mobility.middleware.XMobileMiddleware',
)


def get_middleware(exclude=(), append=(),
                   current={'middleware': MIDDLEWARE_CLASSES}):
    """
    Returns MIDDLEWARE_CLASSES without the middlewares listed in exclude and
    with the middlewares listed in append.

    The use of a mutable dict is intentional, in order to preserve the state of
    the MIDDLEWARE_CLASSES tuple across multiple settings files.
    """

    current['middleware'] = tuple(
        [m for m in current['middleware'] if m not in exclude]
    ) + tuple(append)
    return current['middleware']


INSTALLED_APPS = [
    'constance',
    'constance.backends.database',
    'badgus.base',

    # Local apps
    'compressor',

    'tower',  # for ./manage.py extract (L10n)
    'cronjobs',  # for ./manage.py cron * cmd line tasks
    'django_browserid',


    # Django contrib apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',

    # Third-party apps, patches, fixes
    'commonware.response.cookies',
    'django_nose',
    'session_csrf',

    # L10n
    'product_details',

    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',

    'taggit',
    'valet_keys',

    'badgus.profiles',
    
    'badger',

    'badgus.badger_api',

    'notification',
    #'csp',
    #'south',
]

for app in config('EXTRA_APPS', default='', cast=Csv()):
    INSTALLED_APPS.append(app)

def get_apps(exclude=(), append=(), current={'apps': INSTALLED_APPS}):
    """
    Returns INSTALLED_APPS without the apps listed in exclude and with the apps
    listed in append.

    The use of a mutable dict is intentional, in order to preserve the state of
    the INSTALLED_APPS tuple across multiple settings files.
    """

    current['apps'] = tuple(
        [a for a in current['apps'] if a not in exclude]
    ) + tuple(append)
    return current['apps']

# Path to Java. Used for compress_assets.
JAVA_BIN = '/usr/bin/java'

# Sessions
#
# By default, be at least somewhat secure with our session cookies.
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE',
        default=not DEBUG, cast=bool)
SESSION_COOKIE_HTTPONLY = config('SESSION_COOKIE_HTTPONLY',
        default=not DEBUG, cast=bool)

## Auth
# The first hasher in this list will be used for new passwords.
# Any other hasher in the list can be used for existing passwords.
# Playdoh ships with Bcrypt+HMAC by default because it's the most secure.
# To use bcrypt, fill in a secret HMAC key in your local settings.
BASE_PASSWORD_HASHERS = (
    'django_sha2.hashers.BcryptHMACCombinedPasswordVerifier',
    'django_sha2.hashers.SHA512PasswordHasher',
    'django_sha2.hashers.SHA256PasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.UnsaltedMD5PasswordHasher',
)
HMAC_KEYS = {  # for bcrypt only
    #'2012-06-06': 'cheesecake',
}

from django_sha2 import get_password_hashers
PASSWORD_HASHERS = get_password_hashers(BASE_PASSWORD_HASHERS, HMAC_KEYS)

## Tests
TEST_RUNNER = 'test_utils.runner.RadicalTestSuiteRunner'

# For absolute urls
try:
    DOMAIN = socket.gethostname()
except socket.error:
    DOMAIN = 'localhost'
PROTOCOL = "http://"
PORT = 80

## django-mobility
MOBILE_COOKIE = 'mobile'


##############################
# TODO: Merge the below stuff with the above stuff, since it came from two different settings files
##############################


SITE_TITLE = 'badges-local.allizom.org'

# Make sure South stays out of the way during testing
#SOUTH_TESTS_MIGRATE = False
#SKIP_SOUTH_TESTS = True
SOUTH_MIGRATION_MODULES = {
    'taggit': 'taggit.south_migrations',
}

# Bundles is a dictionary of two dictionaries, css and js, which list css files
# and js files that can be bundled together by the minify app.
MINIFY_BUNDLES = {
    'css': {
        'base': (
            'css/base.css',
        ),
        'example_css': (
            'css/examples/main.css',
        ),
        'example_mobile_css': (
            'css/examples/mobile.css',
        ),
        'bootstrap': (
            'bootstrap/css/bootstrap.css',
            'bootstrap/css/bootstrap-responsive.css',
        )
    },
    'js': {
        'base': (
            'js/libs/jquery-1.7.1.min.js',
            'js/libs/jquery.cookie.js',
            'js/libs/browserid.js',
            'js/base.js',
        ),
        'example_js': (
            'js/examples/libs/jquery-1.4.4.min.js',
            'js/examples/libs/jquery.cookie.js',
            'js/examples/init.js',
        ),
        'bootstrap': (
            'bootstrap/js/bootstrap.js',
        ),
    }
}

# HACK: HMAC_KEYS default to make funfactory happier
HMAC_KEYS = {
    '2011-01-01': 'this is fake; we use persona and do not store passwords',
    '2010-06-01': 'OldSharedKey',
    '2010-01-01': 'EvenOlderSharedKey'
}

# Defines the views served for root URLs.
ROOT_URLCONF = 'badgus.urls'

# Authentication
BROWSERID_CREATE_USER = True
SITE_URL = 'http://localhost:8000'
LOGIN_URL = '/accounts/login'
LOGIN_REDIRECT_URL = '/profiles/home'
LOGIN_REDIRECT_URL_FAILURE = '/'
LOGOUT_REDIRECT_URL = '/'

def username_algo(email):
    from django.contrib.auth.models import User
    cnt, base_name = 0, email.split('@')[0]
    username = base_name
    while User.objects.filter(username=username).count() > 0:
        cnt += 1
        username = '%s_%s' % (base_name, cnt)
    return username

BROWSERID_USERNAME_ALGO = username_algo

AUTHENTICATION_BACKENDS = (
    'django_browserid.auth.BrowserIDBackend',
    'django.contrib.auth.backends.ModelBackend'
)
AUTH_PROFILE_MODULE = "profiles.UserProfile"

TEMPLATE_CONTEXT_PROCESSORS = list(TEMPLATE_CONTEXT_PROCESSORS) + [
    'constance.context_processors.config',
    'django.contrib.messages.context_processors.messages',
    'notification.context_processors.notification',
]

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'
CONSTANCE_DATABASE_CACHE_BACKEND = 'default'

MIDDLEWARE_CLASSES = list(MIDDLEWARE_CLASSES) + [
    'django.contrib.messages.middleware.MessageMiddleware',
    'commonware.response.middleware.StrictTransportMiddleware',
    #'csp.middleware.CSPMiddleware',
]

# Because Jinja2 is the default template loader, add any non-Jinja templated
# apps here:
JINGO_EXCLUDE_APPS = [
    'admin',
    'browserid',
]

def JINJA_CONFIG():
    import jinja2
    config = {
        'extensions': ['jinja2.ext.i18n', 'jinja2.ext.with_',
                       'jinja2.ext.loopcontrols', 'jinja2.ext.autoescape'],
        'finalize': lambda x: x if x is not None else ''
    }
    return config

# Tells the extract script what files to look for L10n in and what function
# handles the extraction. The Tower library expects this.
DOMAIN_METHODS = {
    'messages': [
        ('**/badgus/**.py',
            'tower.management.commands.extract.extract_tower_python'),
        ('**/badgus/**/templates/**.html',
            'tower.management.commands.extract.extract_tower_template')
    ],
}

# Tells the extract script what files to look for L10n in and what function
# handles the extraction. The Tower library expects this.

# # Use this if you have localizable HTML files:
# DOMAIN_METHODS['lhtml'] = [
#    ('**/templates/**.lhtml',
#        'tower.management.commands.extract.extract_tower_template'),
# ]

# # Use this if you have localizable HTML files:
# DOMAIN_METHODS['javascript'] = [
#    # Make sure that this won't pull in strings from external libraries you
#    # may use.
#    ('media/js/**.js', 'javascript'),
# ]

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

# Always generate a CSRF token for anonymous users
ANON_ALWAYS = True

LOGGING = dict(loggers=dict(playdoh = {'level': logging.DEBUG}))

# Django-CSP
CSP_IMG_SRC = ("'self'",
               'http://localhost',
               'http://localhost:8000',
               'http://localhost:8888',
               'http://www.mozilla.org',
               'https://www.mozilla.org',
               'http://beta.openbadges.org',
               'https://beta.openbadges.org',
               'http://backpack.openbadges.org',
               'https://backpack.openbadges.org',
               'http://cf.cdn.vid.ly',
               'http://www.gravatar.com',
               'https://www.gravatar.com',
               'https://secure.gravatar.com',
               'http://chart.apis.google.com',
               'https://chart.apis.google.com',
               'http://plusone.google.com', 'https://plusone.google.com',
               'http://ssl.gstatic.com', 'https://ssl.gstatic.com',
               'http://apis.google.com/', 'https://apis.google.com/')
CSP_STYLE_SRC = ("'self'",
                 'http://localhost',
                 'http://localhost:8000',
                 'http://localhost:8888',
                 'http://www.mozilla.org',
                 'https://www.mozilla.org',
                 'http://beta.openbadges.org',
                 'https://beta.openbadges.org',
                 'http://backpack.openbadges.org',
                 'https://backpack.openbadges.org',
                 'https://fonts.googleapis.com',
                 'http://plusone.google.com', 'https://plusone.google.com',
                 'http://ssl.gstatic.com', 'https://ssl.gstatic.com',
                 'http://apis.google.com', 'https://apis.google.com')
CSP_FONT_SRC = ("'self'",
                'https://themes.googleusercontent.com',)
CSP_SCRIPT_SRC = ("'self'",
                  'http://localhost',
                  'http://localhost:8000',
                  'http://localhost:8888',
                  'http://www.mozilla.org',
                  'https://www.mozilla.org',
                  'http://beta.openbadges.org',
                  'https://beta.openbadges.org',
                  'http://backpack.openbadges.org',
                  'https://backpack.openbadges.org',
                  'http://login.persona.org',
                  'https://login.persona.org',
                  'http://platform.twitter.com', 'https://platform.twitter.com',
                  'http://apis.google.com', 'https://apis.google.com',
                  'http://plusone.google.com', 'https://plusone.google.com',
                  'http://ssl.gstatic.com', 'https://ssl.gstatic.com',
                  'http://connect.facebook.net', 'https://connect.facebook.net',)
CSP_FRAME_SRC = ("'self'",
                 'http://localhost',
                 'http://localhost:8000',
                 'http://localhost:8888',
                 'http://www.mozilla.org',
                 'https://www.mozilla.org',
                 'http://beta.openbadges.org',
                 'https://beta.openbadges.org',
                 'http://backpack.openbadges.org',
                 'https://backpack.openbadges.org',
                 'http://apis.google.com', 'https://apis.google.com',
                 'http://plusone.google.com', 'https://plusone.google.com',
                 'http://ssl.gstatic.com', 'https://ssl.gstatic.com',
                 'http://platform.twitter.com', 'https://platform.twitter.com',
                 'https://www.facebook.com',)
CSP_OPTIONS = ('eval-script',)

BADGER_ALLOW_ADD_BY_ANYONE = config('BADGER_ALLOW_ADD_BY_ANYONE', default=False, cast=bool)

DEFAULT_FROM_EMAIL = 'notifications@badges.mozilla.org'
OBI_BASE_URL = "//backpack.openbadges.org/"
OBI_ISSUER_URL = "//backpack.openbadges.org/issuer.js"

CONSTANCE_CONFIG = dict(
    BADGER_ALLOW_ADD_ONLY_BY_MOZILLIANS = (
        False, 
        'Whether to restrict login to vouched mozillians.org members',
    ),
    MOZILLIANS_API_BASE_URL = (
        'https://mozillians.org/api/v1',
        'Mozillians.org API base URL',
    ),
    MOZILLIANS_API_APPNAME = (
        'badges_mozilla_org',
        'Mozillians.org API app name',
    ),
    MOZILLIANS_API_KEY = (
        '',
        'Mozillians.org API key',
    ),
    MOZILLIANS_API_CACHE_KEY_PREFIX = (
        'mozillians_api',
        'Mozillians.org API result cache key prefix',
    ),
    MOZILLIANS_API_CACHE_TIMEOUT = (
        1800,
        'Mozillians.org API result cache timeout',
    ),
)

BROWSERID_VERIFY_CLASS = 'django_browserid.views.Verify'

SQL_RESET_SEQUENCES = False
