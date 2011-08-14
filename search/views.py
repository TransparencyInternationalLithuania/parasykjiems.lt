import re

from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import Http404
from haystack.query import SearchQuerySet

from search.models import Representative, Institution, Location, Territory
from search.forms import HouseNumberForm
from search import house_numbers


_RESULT_LIMIT = 10

_NORMALISE_RE = re.compile(r'[^\w\s"-]')
_FIND_HOUSE_NUMBER_RE = re.compile(r'(.*)\s(\d+\w?)(:?()$|\s(.*))')


def search(request):
    if 'q' in request.GET and request.GET['q'] != '':
        q = request.GET['q']

        # Remove commas, periods.
        q = _NORMALISE_RE.sub(' ', q)

        m = _FIND_HOUSE_NUMBER_RE.match(q)
        if m:
            pre, num, post = m.group(1, 2, 3)
            q = pre + ' ' + post
        else:
            num = ''

        all_results = SearchQuerySet().auto_query(q)
        more_results = all_results.count() > _RESULT_LIMIT
        results = all_results[:_RESULT_LIMIT]

        # Only set session variable if actually searching. This way
        # the front page can be cached.
        request.session['breadcrumb_search'] = request.get_full_path()
    else:
        q = ''
        num = ''
        results = []
        more_results = False

    return render(request, 'views/search.html', {
        'search_query': request.GET.get('q', ''),
        'house_number': num,
        'results': results,
        'more_results': more_results,
    })


def representative(request, slug):
    rep = get_object_or_404(Representative, slug=slug)
    if not rep.kind.active:
        raise Http404()
    request.session['breadcrumb_choose'] = request.get_full_path()
    return render(request, 'views/representative.html', {
        'representative': rep,
    })


def institution(request, slug):
    inst = get_object_or_404(Institution, slug=slug)
    if not inst.kind.active:
        raise Http404()
    request.session['breadcrumb_choose'] = request.get_full_path()
    return render(request, 'views/institution.html', {
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
    request.session['breadcrumb_choose'] = request.get_full_path()
    return render(request, 'views/location.html', {
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
        request.session['breadcrumb_choose'] = request.get_full_path()

    return render(request, 'views/location_ask.html', {
        'form': form,
    })
