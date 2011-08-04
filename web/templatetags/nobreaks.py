from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter
def nobreaks(value, autoescape=None):
    """This filter turns spaces in a string into &nbsp;s.
    """
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    return mark_safe(esc(value).replace(u' ', u'&nbsp;'))

nobreaks.needs_autoescape = True
