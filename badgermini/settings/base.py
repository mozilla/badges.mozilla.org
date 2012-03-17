# This is your project's main settings file that can be committed to your
# repo. If you need to override a setting locally, use settings_local.py

from funfactory.settings_base import *

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

# Defines the views served for root URLs.
ROOT_URLCONF = 'badgermini.urls'

# Authentication
BROWSERID_CREATE_USER = True
SITE_URL = 'http://localhost:8000'
LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/profiles/home'
LOGIN_REDIRECT_URL_FAILURE = '/'

AUTHENTICATION_BACKENDS = (
    'django_browserid.auth.BrowserIDBackend',
)
AUTH_PROFILE_MODULE = "profiles.UserProfile"

TEMPLATE_CONTEXT_PROCESSORS = list(TEMPLATE_CONTEXT_PROCESSORS) + [
    'django_browserid.context_processors.browserid_form',
]

INSTALLED_APPS = [
    'badgermini.base', # Mainly to override registration templates, FIXME
] + list(INSTALLED_APPS) + [
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',

    'badgermini.profiles',
    
    'badger',
    'badger_multiplayer',

    'csp',
    'django_browserid',
    'south',
]

MIDDLEWARE_CLASSES = list(MIDDLEWARE_CLASSES) + [
    'commonware.response.middleware.StrictTransportMiddleware',
    'csp.middleware.CSPMiddleware',
]

# Because Jinja2 is the default template loader, add any non-Jinja templated
# apps here:
JINGO_EXCLUDE_APPS = [
    'admin',
]

# Tells the extract script what files to look for L10n in and what function
# handles the extraction. The Tower library expects this.
DOMAIN_METHODS = {
    'messages': [
        ('**/badgermini/**.py',
            'tower.management.commands.extract.extract_tower_python'),
        ('**/badgermini/**/templates/**.html',
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
               'http://cf.cdn.vid.ly',
               'https://www.gravatar.com',
               'https://secure.gravatar.com',)
CSP_STYLE_SRC = ("'self'",
                 'http://localhost',
                 'http://localhost:8000',
                 'http://localhost:8888',
                 'http://www.mozilla.org',
                 'https://www.mozilla.org',
                 'http://beta.openbadges.org',
                 'https://beta.openbadges.org',
                 'https://fonts.googleapis.com')
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
                  'http://browserid.org',
                  'https://browserid.org',
                  'https://platform.twitter.com',
                  'https://connect.facebook.net',)
CSP_FRAME_SRC = ("'self'",
                 'http://localhost',
                 'http://localhost:8000',
                 'http://localhost:8888',
                 'http://www.mozilla.org',
                 'https://www.mozilla.org',
                 'http://beta.openbadges.org',
                 'https://beta.openbadges.org',
                 'http://platform.twitter.com',
                 'https://platform.twitter.com',
                 'https://www.facebook.com',)
CSP_OPTIONS = ('eval-script',)
