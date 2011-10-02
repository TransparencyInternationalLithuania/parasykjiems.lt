import time
import re
from urllib2 import urlopen
from BeautifulSoup import BeautifulSoup
import models


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


def get_rep(url, canonic_kind, scrape_kinds, institution):
    soup = get_soup(url)

    tds = soup.find('table', attrs={'class': 'staff'}).findAll('td')
    kind_tds = [td for td in tds if contains_any(td, scrape_kinds)]
    if len(kind_tds):
        tr = kind_tds[0].findParent('tr')
        a = tr.find('a')

        rep, created = models.RepresentativeChange.objects.get_or_create(
            institution=institution,
            kind_name=canonic_kind)
        rep.name = normalise(a.text)
        rep.email = email(a.get('href'))
        rep.phone = normalise(tr.find('td', attrs={'class': 'r'}).text)
    else:
        rep, created = models.RepresentativeChange.objects.get_or_create(
            institution=institution,
            kind_name=canonic_kind)
        rep.delete = True

    rep.save()
    return rep


def delay():
    time.sleep(1)
