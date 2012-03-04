"""
This tag adds GET parameters to the current request URL.

Usage: place this code in your application_dir/templatetags/add_get_parameter.py
In template:
{% load add_get_parameter %}
<a href="{% add_get_paramater param1='val' param2=var %}">
    Link with modified parameters
</a>

This template tag requires 'django.core.context_processors.request' in
TEMPLATE_CONTEXT_PROCESSORS.
"""


import re
from django import template


register = template.Library()


class AddGetParameter(template.Node):
    def __init__(self, values):
        self.values = values

    def render(self, context):
        request = template.resolve_variable('request', context)
        GET = request.GET.copy()
        for key, value in self.values.items():
            if value is None:
                if key in GET:
                    del GET[key]
            else:
                GET[key] = template.Variable(value).resolve(context)

        return '?' + GET.urlencode()


@register.tag
def add_get_parameter(parser, token):
    opts = re.split(r'\s+', token.contents)[1:]
    values = {}
    for opt in opts:
        if opt.startswith('-'):
            k = opt[1:]
            values[k] = None
        else:
            k, v = opt.split('=', 1)
            values[k] = v

    return AddGetParameter(values)
