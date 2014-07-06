from collections import Counter
from django.shortcuts import render, redirect, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.decorators.cache import cache_control
from django.db.models import Q
from haystack.query import SearchQuerySet, SQ

from unidecode import unidecode
from search.models import Institution, Location, Territory, InstitutionKind
from search.forms import HouseNumberForm
from search import house_numbers
from search import utils


import logging
logger = logging.getLogger(__name__)


_RESULT_LIMIT = 16


@cache_control(max_age=60 * 60, public=True)
def search(request):
    if 'q' in request.GET:
        q = request.GET['q']
        terms, num = utils.remove_house_number(q)
    else:
        q = ''
        terms = ''
        num = ''

    if terms.strip() != '':
        sqs = SearchQuerySet()
        clean_terms = sqs.query.clean(terms)
        terms_words = clean_terms.split(u' ')
        terms_butlast = terms_words[:-1]
        terms_last = terms_words[-1]

        # Match all the terms together. Hopefullly this improves
        # result accuracy.
        sq = (SQ(auto=clean_terms) |
              SQ(text=clean_terms) |
              SQ(auto=unidecode(clean_terms)) |
              SQ(text=unidecode(clean_terms)))

        # Match the last word from the auto field, so that it can be
        # matched partially. Also match transliterated version of the
        # word.
        sq = sq | (SQ(auto=terms_last) |
                   SQ(text=terms_last) |
                   SQ(auto=unidecode(terms_last)) |
                   SQ(text=unidecode(terms_last)))

        # AND the rest of the words.
        for w in terms_butlast:
            if w != '':
                sq = sq & (SQ(text=w) | SQ(text=unidecode(w)))

        # If a house number is given, only show results, where a
        # number is relevant.
        if num != '':
            sq = sq & SQ(numbered=True)

        # Separate results by type
        reps = sqs.filter(sq & SQ(django_ct='search.representative'))
        insts = sqs.filter(sq & SQ(django_ct='search.institution'))
        locs = sqs.filter(sq & SQ(django_ct='search.location'))

        all_results = (list(reps[:_RESULT_LIMIT + 1]) +
                       list(insts[:_RESULT_LIMIT + 1]) +
                       list(locs[:_RESULT_LIMIT + 1]))
        more_results = len(all_results) > _RESULT_LIMIT

        logger.info(u'SEARCH ({} results): {}'.format(
            len(all_results), q))

        results = all_results[:_RESULT_LIMIT]
    else:
        results = []
        more_results = False

    results_context = RequestContext(request, {
        'search_query': q,
        'house_number': num,
        'results': results,
        'more_results': more_results,
    })

    results_html = render_to_string('results.html',
                                    results_context)

    if 'results' in request.GET:
        return HttpResponse(results_html)
    elif ('nohist' in request.GET) and (len(results) == 1):
        # 'nohist' is the name of a hidden field in the search
        # form. If the user searches using the form, it means that his
        # browser doesn't support the HTML5 history API, so he's not
        # using incremental search. In that case, if there is only one
        # search result, we redirect to it.
        url = results[0].url
        if num != '':
            url += num + '/'
        return redirect(url)
    else:
        return render(request, 'views/search.html', {
            'search_query': q,
            'results_html': results_html,
        })


def institution(request, slug):
    inst = get_object_or_404(Institution, slug=slug)
    return render(request, 'views/institution.html', {
        'choose_query': '?inst={}'.format(inst.id),
        'institution': inst,
    })


def location(request, slug, house_number=None):
    loc = get_object_or_404(Location, slug=slug)

    # Query not only territories matching the location exactly, but
    # also ones encompassing whole streets and
    # municipalities.
    all_territories = Territory.objects.filter(
        Q(municipality__iexact=loc.municipality,
          elderate__iexact=loc.elderate,
          city__iexact=loc.city,
          street__iexact=loc.street) |
        Q(municipality__iexact=loc.municipality,
          elderate__iexact=loc.elderate,
          city__iexact=loc.city,
          street='') |
        Q(municipality__iexact=loc.municipality,
          elderate__iexact=loc.elderate,
          city='',
          street='') |
        Q(municipality__iexact=loc.municipality,
          elderate='',
          city='',
          street=''))
    territories = list(all_territories.filter(numbers=''))
    restricted_territories = all_territories.exclude(numbers='')
    if restricted_territories.exists():
        if house_number:
            for rt in restricted_territories:
                if house_numbers.territory_contains(rt, house_number):
                    territories.append(rt)
        else:
            return redirect(reverse(location_ask, args=[slug]))
    institutions = [t.institution for t in territories]
    institutions.sort(key=lambda i: i.kind.ordinal)

    kind_id_counts = Counter(i.kind.id
                             for i in institutions).iteritems()
    repeated_kinds = [InstitutionKind.objects.get(id=kid)
                      for kid, count in kind_id_counts
                      if count > 1]
    if repeated_kinds != []:
        logger.warning('More than one institution of same kind {} at {}, '
                       'house number {}.'
                       .format(repeated_kinds, loc, house_number))

    num_q = '&n={}'.format(house_number) if house_number else ''

    if loc.street:
        title = loc.street
        if house_number and house_number != '':
            title += ' ' + house_number
        title += ', ' + loc.city
    else:
        title = ', '.join([x for x in
                           [loc.city,
                           loc.elderate,
                           loc.municipality]
                           if x])

    return render(request, 'views/location.html', {
        'choose_query': '?loc={}{}'.format(loc.id, num_q),
        'title': title,
        'institutions': institutions,
        'repeated_kinds': repeated_kinds,
    })


@cache_control(public=False)
def location_ask(request, slug):
    if request.method == 'POST':
        form = HouseNumberForm(request.POST)
        if form.is_valid():
            return redirect(reverse(location,
                                    args=[slug,
                                          form.cleaned_data['house_number']]))
    else:
        form = HouseNumberForm()

    return render(request, 'views/location_ask.html', {
        'form': form,
    })
