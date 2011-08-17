from django.shortcuts import render, redirect, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from haystack.query import SearchQuerySet

from search.models import Representative, Institution, Location, Territory
from search.forms import HouseNumberForm
from search import house_numbers
from search import utils


import logging
logger = logging.getLogger(__name__)


_RESULT_LIMIT = 10


def _render_results(request):
    if 'q' in request.GET and request.GET['q'] != '':
        q = request.GET['q']

        q, num = utils.remove_house_number(q)

        all_results = SearchQuerySet().auto_query(q)
        result_count = all_results.count()

        if result_count == 1:
            result = all_results[0]
            url = result.url
            if num != '' and result.content_type() == 'search.location':
                url += num + '/'

        more_results = result_count > _RESULT_LIMIT
        results = all_results[:_RESULT_LIMIT]
    else:
        q = ''
        num = ''
        results = []
        more_results = False

    context = RequestContext(request, {
        'search_query': request.GET.get('q', ''),
        'house_number': num,
        'results': results,
        'more_results': more_results,
    })

    return render_to_string('results.html', context)


def search(request):
    return render(request, 'views/search.html', {
        'search_query': request.GET.get('q', ''),
        'results_html': _render_results(request),
    })


def results(request):
    return HttpResponse(_render_results(request))


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
        municipality=loc.municipality,
        elderate=loc.elderate,
        city=loc.city,
        street=loc.street)
    territories = list(all_territories.filter(numbers=''))
    restricted_territories = all_territories.exclude(numbers='')
    if restricted_territories.exists():
        if house_number:
            for rt in restricted_territories:
                if house_numbers.territory_contains(rt, house_number):
                    territories.append(rt)
        else:
            return redirect(reverse(location_ask, args=[slug]))
    institutions = [t.institution
                    for t in territories
                    if t.institution.kind.active]
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
