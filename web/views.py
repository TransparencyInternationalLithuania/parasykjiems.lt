import logging

from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist
import django.http
from haystack.query import SearchQuerySet

from web.models import Representative, Institution, Location, Territory


def index(request):
    if 'q' in request.GET and request.GET['q'] != '':
        q = request.GET['q']
        results = SearchQuerySet().auto_query(q)
    else:
        q = ''
        results = []

    return render(request, 'index.html', {
        'search_query': q,
        'results': results,
        'active_menu': _('Representative search'),
    })


def letters(request):
    return render(request, 'letters.html', {
        'active_menu': _('Public letters'),
    })


def about(request):
    return render(request, 'about.html', {
        'active_menu': _('About project'),
    })


def representative(request, rep_id):
    try:
        rep = Representative.objects.get(id=rep_id)
        return render(request, 'representative.html', {
            'representative': rep,
            'active_menu': _('Representative search'),
        })
    except ObjectDoesNotExist:
        return django.http.HttpResponseNotFound(_('Representative not found'))


def institution(request, inst_id):
    try:
        inst = Institution.objects.get(id=inst_id)
        reps = Representative.objects.filter(institution=inst)
        return render(request, 'institution.html', {
            'institution': inst,
            'representatives': reps,
            'active_menu': _('Representative search'),
        })
    except ObjectDoesNotExist:
        return django.http.HttpResponseNotFound(_('Institution not found'))


def location(request, loc_id, house_number=None):
    try:
        loc = Location.objects.get(id=loc_id)
        # territories = Territory.objects.filter(
        # if house_number:
        # else:
        #     pass
    except ObjectDoesNotExist:
        return django.http.HttpResponseNotFound(_('Location not found'))


def setlang(request):
    language = request.GET.get('lang', 'lt')
    back = request.META.get('HTTP_REFERER', '/')
    response = django.http.HttpResponseRedirect(back)
    request.session['django_language'] = language
    return response
