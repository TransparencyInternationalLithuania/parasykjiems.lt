import re
from django.http import QueryDict
from django.core.exceptions import ObjectDoesNotExist

from models import Location, Representative, Institution

import logging
logger = logging.getLogger(__name__)


_REMOVE_PUNCTUATION_RE = re.compile(ur'[^\w/ -]', flags=re.UNICODE)
_NORMALISE_SPACES_RE = re.compile(ur'(\s)\s+')

_FIND_HOUSE_NUMBER_RE = re.compile(
    ur'''
    (.*\s|)
    ( \d+\w? ) (?: / \d+\w? )?
    (\s.*|)
    $
    ''',
    flags=re.UNICODE | re.VERBOSE)


def remove_house_number(q):
    """Removes house number from search query string.

    Returns duple of new search query string and extracted house
    number (as a string). If the string doesn't contain a house
    number, returns '' instead.
    """
    q = _REMOVE_PUNCTUATION_RE.sub(u' ', q)

    m = _FIND_HOUSE_NUMBER_RE.match(q)
    if m:
        pre, num, post = m.group(1, 2, 3)
        q = pre + post
    else:
        num = u''

    q = _NORMALISE_SPACES_RE.sub(u' ', q)

    return q.strip(), num


_REMOVE_DASHES_RE = re.compile(ur'-')


class ChoiceState:
    """Represents the user's choice of location (possibly with house
    number), institution and/or representative.

    Allows easily converting to and from query strings.
    """
    def __init__(self,
                 query=None,
                 loc=None, n=None,
                 inst=None, rep=None):
        self.loc = loc
        self.n = n
        self.inst = inst
        self.rep = rep
        if query:
            if isinstance(query, basestring):
                query = QueryDict(query)
            try:
                if not rep and 'rep' in query:
                    self.rep = Representative.objects.get(
                        id=int(query['rep']))
                if not inst and 'inst' in query:
                    self.inst = Institution.objects.get(
                        id=int(query['inst']))
                if not loc and 'loc' in query:
                    self.loc = Location.objects.get(
                        id=int(query['loc']))
                    self.n = query.get('n', None)
            except Exception as e:
                logger.warning("Can't make ChoiceState({}, {}, {}, {}, {}): {}"
                               .format(
                                   repr(query), repr(loc), repr(n),
                                   repr(inst), repr(rep),
                                   e))

    def add_recipient(self, recipient):
        if isinstance(recipient, Representative):
            self.rep = recipient
        else:
            self.inst = recipient

    def choose_url(self):
        if self.loc:
            url = self.loc.get_absolute_url()
            if self.n:
                url += self.n + '/'
            return url
        elif self.inst or self.rep:
            return (self.inst or self.rep).get_absolute_url()
        else:
            return '#'

    def write_url(self):
        if self.inst or self.rep:
            return '/write' + (self.inst or self.rep).get_absolute_url()
        else:
            return '#'

    def query_string(self):
        q = QueryDict('').copy()
        if self.loc:
            q['loc'] = self.loc.id
            if self.n:
                q['n'] = self.n
        if self.inst:
            q['inst'] = self.inst.id
        if self.rep:
            q['rep'] = self.rep.id
        return q.urlencode()
