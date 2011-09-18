from django import template
from web.models import Snippet

import logging
logger = logging.getLogger(__name__)


register = template.Library()


class SnippetNode(template.Node):
    def __init__(self, name, plain):
        self.name = name
        self.plain = plain

    def render(self, context):
        try:
            snippet = Snippet.objects.get(name=self.name)
            if self.plain:
                return snippet.body
            else:
                return snippet.body_rendered
        except Exception as e:
            logger.error("Can't display snippet {}: {}".format(
                repr(self.name), e))
            return ''


@register.tag
def snippet(parser, token):
    """Usage: {% snippet "snippet-identifier" [plain] %}

    If the plain parameter is given, don't markdown the snippet.
    """
    try:
        # split_contents() knows not to split quoted strings.
        tokens = token.split_contents()
        tag_name = tokens[0]
        snippet_name = tokens[1]
        if len(tokens) >= 3 and 'plain' in tokens[2:]:
            plain = True
        else:
            plain = False
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires one or two arguments" % token.contents.split()[0])
    if not (snippet_name[0] == snippet_name[-1] and
            snippet_name[0] in ('"', "'")):
        raise template.TemplateSyntaxError(
            "%r tag's argument should be in quotes" % tag_name)
    return SnippetNode(snippet_name[1:-1], plain)
