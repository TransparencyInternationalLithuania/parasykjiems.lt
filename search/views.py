from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import Http404
from haystack.query import SearchQuerySet

from search.models import Representative, Institution, Location, Territory
from search.forms import HouseNumberForm
from search import house_numbers
from slug import slug_get_or_404


_RESULT_LIMIT = 10

def search(request):
    request.session['breadcrumb_search'] = request.path
    if 'q' in request.GET and request.GET['q'] != '':
        q = request.GET['q']
        all_results = SearchQuerySet().auto_query(q)
        more_results = all_results.count() > _RESULT_LIMIT
        results = all_results[:_RESULT_LIMIT]
        request.session['breadcrumb_search'] += u'?q=' + q
    else:
        q = ''
        results = []
        more_results = False

    return render(request, 'views/search.html', {
        'search_query': q,
        'results': results,
        'more_results': more_results,
    })


def representative(request, id):
    rep = slug_get_or_404(Representative, id)
    if not rep.kind.active:
        raise Http404()
    request.session['breadcrumb_choose'] = request.path
    return render(request, 'views/representative.html', {
        'representative': rep,
    })


def institution(request, id):
    inst = slug_get_or_404(Institution, id)
    if not inst.kind.active:
        raise Http404()
    request.session['breadcrumb_choose'] = request.path
    return render(request, 'views/institution.html', {
        'institution': inst,
    })


def location(request, id, house_number=None):
    loc = slug_get_or_404(Location, id)
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
            return redirect(reverse(location_ask, args=[id]))
    institutions = [t.institution
                    for t in territories
                    if t.institution.kind.active]
    institutions.sort(key=lambda i: i.kind.ordinal)
    request.session['breadcrumb_choose'] = request.path
    return render(request, 'views/location.html', {
        'institutions': institutions,
    })


def location_ask(request, id):
    if request.method == 'POST':
        form = HouseNumberForm(request.POST)
        if form.is_valid():
            return redirect(reverse(location,
                                    args=[id,
                                          form.cleaned_data['house_number']]))
    else:
        form = HouseNumberForm()
        request.session['breadcrumb_choose'] = request.path

    return render(request, 'views/location_ask.html', {
        'form': form,
    })
