from jingo import register
import jinja2


# TODO: Allow configurable whitelists
ALLOWED_TAGS = [
    'a', 'abbr', 'br', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'img', 'li',
    'ol', 'p', 'strong', 'ul'
]

ALLOWED_ATTRIBUTES = {
    "img": ["src"]
}

@register.filter
def bleach_markup(val):
    """Template filter to linkify and clean content expected to allow HTML"""
    try:
        import bleach
        val = val.replace('\n', '<br />')
        val = bleach.linkify(val)
        val = bleach.clean(val,
                           tags=ALLOWED_TAGS,
                           attributes=ALLOWED_ATTRIBUTES)
        return jinja2.Markup(val)
    except ImportError:
        return val
