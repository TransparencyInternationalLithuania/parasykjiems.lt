import re
from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter
def email_blockquote(value, autoescape=None):
    """Turn quotes in an email message into HTML blockquotes.
    """
    def process(text):
        # The actual processing
        lines = []
        blockquote_level = 0
        QUOTE_LINE_RE = re.compile(r'^\s*((?:(?:&gt;|>)\s*)*)(.*)')
        for line in text.split('\n'):
            line = line.strip()
            if line == '-----Original Message-----':
                blockquote_level += 1
                lines.append('<blockquote>')
            else:
                m = QUOTE_LINE_RE.match(line)
                assert(m)
                angles, clean_line = m.group(1), m.group(2)
                angle_count = angles.replace('&gt;', '>').count('>')
                diff = angle_count - blockquote_level
                if diff > 0:
                    quote_tags = '<blockquote>' * diff
                elif diff < 0:
                    quote_tags = '</blockquote>' * (-diff)
                else:
                    quote_tags = ''
                blockquote_level = angle_count
                lines.append(quote_tags + clean_line)
        lines.append('</blockquote>' * blockquote_level)
        print lines
        return '\n'.join(lines)

    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    return mark_safe(process(esc(value)))

email_blockquote.needs_autoescape = True
