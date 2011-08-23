from django.shortcuts import render, redirect, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from haystack.query import SearchQuerySet, SQ
from unidecode import unidecode

from search.models import Representative, Institution, Location, Territory
from search.forms import HouseNumberForm
from search import house_numbers
from search import utils


import logging
logger = logging.getLogger(__name__)


_RESULT_LIMIT = 10


def search(request):
    if 'q' in request.GET and request.GET['q'] != '':
        q = request.GET['q']

        q, num = utils.remove_house_number(q)

        sqs = SearchQuerySet()
        clean_q = sqs.query.clean(q)
        q_words = clean_q.split(u' ')
        q_butlast = q_words[:-1]
        q_last = q_words[-1]

        # Match the last word from the auto field, so that it can be
        # matched partially.
        sq = SQ(auto=q_last) | SQ(text=q_last)

        # AND the rest of the words.
        for w in q_butlast:
            sq = sq & SQ(text=w)

        # If a house number is given, only show results, where a
        # number is relevant.
        if num != '':
            sq = sq & SQ(numbered=True)

        all_results = sqs.filter(sq)
        more_results = all_results.count() > _RESULT_LIMIT

        results = all_results[:_RESULT_LIMIT]
    else:
        q = ''
        num = ''
        results = []
        more_results = False

    results_context = RequestContext(request, {
        'search_query': request.GET.get('q', ''),
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
            'search_query': request.GET.get('q', ''),
            'results_html': results_html,
        })


def representative(request, slug):
    rep = get_object_or_404(Representative, slug=slug)
    if not rep.kind.active:
        raise Http404()
    return render(request, 'views/representative.html', {
        'representative': rep,
    })


def institution(request, slug):
    inst = get_object_or_404(Institution, slug=slug)
    if not inst.kind.active:
        raise Http404()
    return render(request, 'views/institution.html', {
        'choose_query': '?inst={}'.format(inst.id),
        'institution': inst,
    })


def location(request, slug, house_number=None):
    loc = get_object_or_404(Location, slug=slug)
    all_territories = Territory.objects.filter(
        municipality__iexact=loc.municipality,
        elderate__iexact=loc.elderate,
        city__iexact=loc.city,
        street__iexact=loc.street)
    territories = list(all_territories.filter(numbers=''))
    restricted_territories = all_territories.exclude(numbers='')
    if restricted_territories.exists():
        if house_number:
            for rt in restricted_territories:
                if house_numbers.territory_contains(rt, house_number):
                    territories.append(rt)
        else:
            return redirect(reverse(location_ask, args=[slug]))
    institutions = ([t.institution
                     for t in territories
                     if t.institution.kind.active]
                    + list(Institution.objects.filter(
                        name__iexact=loc.municipality)))
    institutions.sort(key=lambda i: i.kind.ordinal)
    num_q = '&n={}'.format(house_number) if house_number else ''
    return render(request, 'views/location.html', {
        'choose_query': '?loc={}{}'.format(loc.id, num_q),
        'institutions': institutions,
    })


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
