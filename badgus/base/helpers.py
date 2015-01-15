import datetime
import urllib
import urlparse

from django.contrib.staticfiles.storage import staticfiles_storage
from django.template import defaultfilters
from django.utils.encoding import smart_str
from django.utils.html import strip_tags

from jingo import register
import jinja2

from .urlresolvers import reverse

from django.conf import settings


# Yanking filters from Django.
register.filter(strip_tags)
register.filter(defaultfilters.timesince)
register.filter(defaultfilters.truncatewords)


@register.function
def thisyear():
    """The current year."""
    return jinja2.Markup(datetime.date.today().year)


@register.function
def url(viewname, *args, **kwargs):
    """Helper for Django's ``reverse`` in templates."""
    return reverse(viewname, args=args, kwargs=kwargs)


@register.filter
def urlparams(url_, hash=None, **query):
    """Add a fragment and/or query paramaters to a URL.

    New query params will be appended to exising parameters, except duplicate
    names, which will be replaced.
    """
    url = urlparse.urlparse(url_)
    fragment = hash if hash is not None else url.fragment

    # Use dict(parse_qsl) so we don't get lists of values.
    q = url.query
    query_dict = dict(urlparse.parse_qsl(smart_str(q))) if q else {}
    query_dict.update((k, v) for k, v in query.items())

    query_string = _urlencode([(k, v) for k, v in query_dict.items()
                               if v is not None])
    new = urlparse.ParseResult(url.scheme, url.netloc, url.path, url.params,
                               query_string, fragment)
    return new.geturl()


def _urlencode(items):
    """A Unicode-safe URLencoder."""
    try:
        return urllib.urlencode(items)
    except UnicodeEncodeError:
        return urllib.urlencode([(k, smart_str(v)) for k, v in items])


@register.filter
def urlencode(txt):
    """Url encode a path."""
    if isinstance(txt, unicode):
        txt = txt.encode('utf-8')
    return urllib.quote_plus(txt)


@register.function
def static(path):
    return staticfiles_storage.url(path)

if hasattr(settings, 'BLEACH_ALLOWED_TAGS'):
    ALLOWED_TAGS = settings.BLEACH_ALLOWED_TAGS
else:
    ALLOWED_TAGS = [
        'a', 'abbr', 'br', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'img', 'li',
        'ol', 'p', 'strong', 'ul', 'dl', 'dt', 'dd',
        'pre', 'code', 'cite',
        'dl', 'dt', 'dd', 'small', 'sub', 'sup', 'u', 'strike', 'samp',
        'table', 'tbody', 'thead', 'tfoot', 'tr', 'th', 'td', 'colgroup', 'col',
    ]

if hasattr(settings, 'BLEACH_ALLOWED_ATTRIBUTES'):
    ALLOWED_ATTRIBUTES = settings.BLEACH_ALLOWED_ATTRIBUTES
else:
    ALLOWED_ATTRIBUTES = {
        '*': ['style'],
        'img': ['width', 'height', 'src', 'alt'],
        'a': ['href', 'title'],
    }

if hasattr(settings, 'BLEACH_ALLOWED_STYLES'):
    ALLOWED_STYLES = settings.BLEACH_ALLOWED_STYLES
else:
    ALLOWED_STYLES = [
        'width', 'height'
    ]


@register.filter
def bleach_markup(val, nltobr=True, linkify=True):
    """Template filter to linkify and clean content expected to allow HTML"""
    try:
        import bleach
        if nltobr:
            val = val.replace('\n', '<br />')
        if linkify:
            val = bleach.linkify(val)
        val = bleach.clean(val,
                           tags=ALLOWED_TAGS,
                           attributes=ALLOWED_ATTRIBUTES,
                           styles=ALLOWED_STYLES)
        return jinja2.Markup(val)
    except ImportError:
        # If bleach is unavailable, just silently punt.
        return val
