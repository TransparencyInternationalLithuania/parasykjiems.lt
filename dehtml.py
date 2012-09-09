from HTMLParser import HTMLParser
from re import sub
import sys


_IGNORE_TAGS = frozenset(['head', 'script', 'style'])


class _DeHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self._text = []
        self._ignore = False
        self._href = None
        self._a_text = None

    def handle_data(self, data):
        if not self._ignore:
            text = data.strip()
            if len(text) > 0:
                text = sub(ur'[ \t\r\n]+', ' ', text)
                self._text.append(text + ' ')
                if self._href:
                    self._a_text.append(text)

    def handle_starttag(self, tag, attrs):
        if not self._ignore:
            if tag == u'p':
                self._text.append(u'\n\n')
            elif tag == u'br':
                self._text.append(u'\n')
            elif tag == u'a':
                self._href = sub(ur'^mailto:', u'', dict(attrs)[u'href']).strip()
                self._a_text = []
            elif tag in _IGNORE_TAGS:
                self._ignore = True

    def handle_startendtag(self, tag, attrs):
        if not self._ignore:
            if tag == u'br':
                self._text.append(u'\n\n')

    def handle_endtag(self, tag):
        if self._ignore and tag in _IGNORE_TAGS:
            self._ignore = False
        elif tag == u'a' and self._href:
            a_text = u''.join(self._a_text).strip()
            if a_text != self._href and self._href.startswith('http:') or '@' in self._href:
                self._text.append(u'({}) '.format(self._href))
            self._href = None
            self._a_text = None

    def text(self):
        return u''.join(self._text).strip()


def dehtml(text):
    if isinstance(text, str):
        text = text.decode('utf-8')

    parser = _DeHTMLParser()
    parser.feed(text)
    parser.close()
    return parser.text()


def main():
    print dehtml(sys.stdin.read()).encode('utf-8')


if __name__ == '__main__':
    main()
