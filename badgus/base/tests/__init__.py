from django.conf import settings, UserSettingsHolder
from django.utils.functional import wraps

from constance import config as c_config
from constance.backends import database as constance_database


class FakeResponse:
    """Quick and dirty mocking stand-in for a response object"""
    def __init__(self, **entries):
        self.__dict__.update(entries)

    def read(self):
        return self.content


class overrider(object):
    """
    See http://djangosnippets.org/snippets/2437/

    Acts as either a decorator, or a context manager.  If it's a decorator it
    takes a function and returns a wrapped function.  If it's a contextmanager
    it's used with the ``with`` statement.  In either event entering/exiting
    are called before and after, respectively, the function/block is executed.
    """
    def __init__(self, **kwargs):
        self.options = kwargs

    def __enter__(self):
        self.enable()

    def __exit__(self, exc_type, exc_value, traceback):
        self.disable()

    def __call__(self, func):
        @wraps(func)
        def inner(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return inner

    def enable(self):
        pass

    def disable(self):
        pass


class override_constance_settings(overrider):
    """Decorator / context manager to override constance settings and defeat
    its caching."""

    def enable(self):
        #self.old_cache = constance_database.db_cache
        #constance_database.db_cache = None
        self.old_settings = dict((k, getattr(c_config, k))
                                 for k in dir(c_config))
        for k, v in self.options.items():
            c_config._backend.set(k, v)

    def disable(self):
        for k, v in self.old_settings.items():
            c_config._backend.set(k, v)
        #constance_database.db_cache = self.old_cache


class override_settings(overrider):
    """Decorator / context manager to override Django settings"""

    def enable(self):
        self.old_settings = settings._wrapped
        override = UserSettingsHolder(settings._wrapped)
        for key, new_value in self.options.items():
            setattr(override, key, new_value)
        settings._wrapped = override

    def disable(self):
        settings._wrapped = self.old_settings

