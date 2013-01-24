from jingo import register
import jinja2

from django.conf import settings


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
