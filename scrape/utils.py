import time
import re
from urllib2 import urlopen
from BeautifulSoup import BeautifulSoup


_MULTIPLE_SPACES = re.compile(r'\s\s+')
_NBSP = u'\xa0'


def normalise(s):
    return _MULTIPLE_SPACES.sub(' ', s.replace(_NBSP, ' ').strip())


def email(s):
    if s.startswith('mailto:'):
        return s[len('mailto:'):]
    else:
        return s


def get_soup(url):
    response = urlopen(url)
    return BeautifulSoup(response, convertEntities=BeautifulSoup.HTML_ENTITIES)


def contains_any(s, substrings):
    return any(substring in s for substring in substrings)


def delay():
    time.sleep(1)
