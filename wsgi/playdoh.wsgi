import os
import site

os.environ.setdefault('CELERY_LOADER', 'django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'badgus.settings')

# Add the app dir to the python path so we can import manage.
wsgidir = os.path.dirname(__file__)
site.addsitedir(os.path.abspath(os.path.join(wsgidir, '../')))

# Activate virtualenv
activate_env = os.path.abspath(os.path.join(wsgidir, "../virtualenv/bin/activate_this.py"))
execfile(activate_env, dict(__file__=activate_env))

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

# vim: ft=python
