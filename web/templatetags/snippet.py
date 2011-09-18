from django import template
from web.models import Snippet

import logging
logger = logging.getLogger(__name__)


register = template.Library()


class SnippetNode(template.Node):
    def __init__(self, name):
        self.name = name

    def render(self, context):
        try:
            snippet = Snippet.objects.get(name=self.name)
            return snippet.body_rendered
        except Exception as e:
            logger.error("Can't display snippet {}: {}".format(
                repr(self.name), e))
            return ''


@register.tag
def snippet(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, snippet_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires a single argument" % token.contents.split()[0])
    if not (snippet_name[0] == snippet_name[-1] and
            snippet_name[0] in ('"', "'")):
        raise template.TemplateSyntaxError(
            "%r tag's argument should be in quotes" % tag_name)
    return SnippetNode(snippet_name[1:-1])
