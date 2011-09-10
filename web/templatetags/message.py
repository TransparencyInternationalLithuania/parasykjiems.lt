from django import template
from web.models import Message
import markdown


register = template.Library()


class MessageNode(template.Node):
    def __init__(self, name):
        self.message = Message.objects.get(name=name)

    def render(self, context):
        return markdown.markdown(self.message.body)


@register.tag
def do_message(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, message_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires a single argument" % token.contents.split()[0])
    if not (message_name[0] == message_name[-1] and
            message_name[0] in ('"', "'")):
        raise template.TemplateSyntaxError(
            "%r tag's argument should be in quotes" % tag_name)
    return MessageNode(message_name[1:-1])
