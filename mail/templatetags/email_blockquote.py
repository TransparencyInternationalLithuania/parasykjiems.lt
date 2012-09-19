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
        output = []
        blockquote_level = 0
        outlook_quote = False

        # This regexp captures two groups: the beginning of the line
        # consisting only of spaces and '>' characters and the rest of
        # the line.
        QUOTE_LINE_RE = re.compile(r'((?:(?:&gt;|>)\s*)*)(.*)')

        for line in text.split('\n'):
            line = line.strip()
            if line == '-----Original Message-----':
                # Outlook quotes are handled separately because they
                # dont have '>'s.
                outlook_quote = True
                output.append('<blockquote>')
            else:
                m = QUOTE_LINE_RE.match(line)
                assert(m)
                angles, clean_line = m.group(1), m.group(2)

                # Count the '>'s.
                angle_count = angles.replace('&gt;', '>').count('>')

                # Open or close blockquotes if the amount of '>'s
                # changes with respect to the previous line.
                diff = angle_count - blockquote_level
                if diff > 0:
                    output.append('<blockquote>' * diff)
                elif diff < 0:
                    output.append('</blockquote>' * (-diff))
                blockquote_level = angle_count

                output.append(clean_line + '\n')

        # Close any open blockquote tags including the outlook one.
        output.append('</blockquote>' * blockquote_level)
        if outlook_quote:
            output.append('</blockquote>')

        return ''.join(output)

    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    return mark_safe(process(esc(value)))

email_blockquote.needs_autoescape = True
