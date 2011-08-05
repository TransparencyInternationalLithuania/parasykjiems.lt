from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import Http404
from haystack.query import SearchQuerySet

from search.models import Representative, Institution, Location, Territory
from search.forms import HouseNumberForm
from search import house_numbers


def search(request):
    request.session['breadcrumb_search'] = request.path
    if 'q' in request.GET and request.GET['q'] != '':
        q = request.GET['q']
        results = SearchQuerySet().auto_query(q)
        request.session['breadcrumb_search'] += u'?q=' + q
    else:
        q = ''
        results = []

    return render(request, 'views/search.html', {
        'search_query': q,
        'results': results,
    })


def representative(request, rep_id):
    rep = get_object_or_404(Representative, id=rep_id)
    if not rep.kind.active:
        raise Http404()
    request.session['breadcrumb_choose'] = request.path
    return render(request, 'views/representative.html', {
        'representative': rep,
    })


def institution(request, inst_id):
    inst = get_object_or_404(Institution, id=inst_id)
    if not inst.kind.active:
        raise Http404()
    request.session['breadcrumb_choose'] = request.path
    return render(request, 'views/institution.html', {
        'institution': inst,
    })


def location(request, loc_id, house_number=None):
    loc = get_object_or_404(Location, id=loc_id)
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
            return redirect(reverse(location_ask, args=[loc_id]))
    institutions = [t.institution
                    for t in territories
                    if t.institution.kind.active]
    request.session['breadcrumb_choose'] = request.path
    return render(request, 'views/location.html', {
        'institutions': institutions,
    })


def location_ask(request, loc_id):
    if request.method == 'POST':
        form = HouseNumberForm(request.POST)
        if form.is_valid():
            return redirect(reverse(location,
                                    args=[loc_id,
                                          form.cleaned_data['house_number']]))
    else:
        form = HouseNumberForm()
        request.session['breadcrumb_choose'] = request.path

    return render(request, 'views/location_ask.html', {
        'form': form,
    })
